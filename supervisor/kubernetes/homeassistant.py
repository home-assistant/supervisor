"""Kubernetes backend for Home Assistant Core.

This is a minimal implementation to run Home Assistant Core on Kubernetes using:
- A single StatefulSet (replicas 0/1)
- A ClusterIP Service for stable networking
- A shared RWX PVC mounted at /config via subPath

This backend intentionally does not support host-level integrations.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from ipaddress import IPv4Address
import logging
import os
import re
from typing import Any, TYPE_CHECKING

from atomicwrites import atomic_write
from kubernetes_asyncio import client

from ..docker.const import ENV_TIME, ENV_TOKEN, ENV_TOKEN_OLD
from ..exceptions import HomeAssistantError, KubernetesError, KubernetesNotFound
from .const import (
    DEFAULT_SUPERVISOR_K8S_HA_TRUSTED_PROXIES,
    ENV_SUPERVISOR_K8S_HA_TRUSTED_PROXIES,
)

if TYPE_CHECKING:
    from awesomeversion import AwesomeVersion

    from ..coresys import CoreSys


_LOGGER: logging.Logger = logging.getLogger(__name__)

_RE_HTTP_SECTION: re.Pattern[str] = re.compile(r"(?m)^http:\s*$")


@dataclass(slots=True, frozen=True)
class KubeHomeAssistantNames:
    """Kubernetes resource names for Home Assistant Core."""

    statefulset: str
    service: str
    headless_service: str


class KubernetesHomeAssistant:
    """Kubernetes workload implementation for Home Assistant Core."""

    def __init__(self, coresys: CoreSys) -> None:
        self.coresys = coresys
        self._names = KubeHomeAssistantNames(
            statefulset="homeassistant",
            service="homeassistant",
            headless_service="homeassistant-headless",
        )
        self._cluster_ip: IPv4Address = IPv4Address("0.0.0.0")

    @property
    def name(self) -> str:
        return self._names.statefulset

    @property
    def image(self) -> str:
        return self.coresys.homeassistant.image

    @property
    def version(self) -> AwesomeVersion | None:
        return self.coresys.homeassistant.version

    @property
    def arch(self) -> str | None:
        # Keep existing semantics: Supervisor arch handling is separate.
        return self.coresys.arch.default

    @property
    def machine(self) -> str | None:
        # Do not call back into HomeAssistant.module.machine (it delegates to
        # core.instance.machine), otherwise we recurse.
        return self.coresys.machine or "kubernetes"

    @property
    def ip_address(self) -> IPv4Address:
        return self._cluster_ip

    @property
    def in_progress(self) -> bool:
        return False

    async def attach(self, *, version: AwesomeVersion, skip_state_event_if_down: bool = False) -> None:
        """Attach to existing Kubernetes resources."""
        if not await self.exists():
            raise KubernetesNotFound("Home Assistant is not installed")
        await self._refresh_cluster_ip()

    async def exists(self) -> bool:
        """Return True if the StatefulSet exists."""
        namespace = self.coresys.kubernetes.context.namespace
        try:
            await self.coresys.kubernetes.apps.read_namespaced_stateful_set(
                name=self._names.statefulset, namespace=namespace
            )
        except client.ApiException as err:
            if err.status == 404:
                return False
            raise KubernetesError(
                f"Unable to read StatefulSet {namespace}/{self._names.statefulset}: {err}"
            ) from err
        return True

    async def is_running(self) -> bool:
        """Return True if the Home Assistant pod is Ready."""
        namespace = self.coresys.kubernetes.context.namespace
        selector = "io.hass.type=core,io.hass.managed=true"
        pods = await self.coresys.kubernetes.core.list_namespaced_pod(
            namespace=namespace, label_selector=selector
        )
        for pod in pods.items:
            for cond in pod.status.conditions or []:
                if cond.type == "Ready" and cond.status == "True":
                    return True
        return False

    async def install(self, version: AwesomeVersion, *, image: str) -> None:
        """Create or patch the Home Assistant StatefulSet and Service."""
        changed = await self._ensure_reverse_proxy_config()

        namespace = self.coresys.kubernetes.context.namespace
        labels = {
            "io.hass.type": "core",
            "io.hass.managed": "true",
        }

        full_image = f"{image}:{version}"
        volume_name = "hassio-data"

        env = [
            client.V1EnvVar(name=ENV_TIME, value=self.coresys.timezone),
            client.V1EnvVar(name=ENV_TOKEN, value=self.coresys.homeassistant.supervisor_token),
            client.V1EnvVar(
                name=ENV_TOKEN_OLD, value=self.coresys.homeassistant.supervisor_token
            ),
            # Align with what HA expects for supervisor integration.
            client.V1EnvVar(
                name="SUPERVISOR",
                # Home Assistant expects a hostname/IP, not a URL.
                # It will build the URL internally (http://<host>:80).
                value=self.coresys.kubernetes.context.service_supervisor,
            ),
            client.V1EnvVar(
                name="HASSIO",
                # Home Assistant expects a hostname/IP, not a URL.
                value=self.coresys.kubernetes.context.service_supervisor,
            ),
        ]

        volumes = [
            client.V1Volume(
                name=volume_name,
                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                    claim_name=self.coresys.kubernetes.context.shared_pvc_claim
                ),
            )
        ]
        volume_mounts = [
            client.V1VolumeMount(
                name=volume_name,
                mount_path="/config",
                sub_path="homeassistant",
            )
        ]

        container = client.V1Container(
            name="homeassistant",
            image=full_image,
            env=env,
            ports=[client.V1ContainerPort(container_port=8123)],
            volume_mounts=volume_mounts,
        )

        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels=labels),
            spec=client.V1PodSpec(containers=[container], volumes=volumes),
        )

        # Preserve replica count if it exists
        replicas = 1
        try:
            existing = await self.coresys.kubernetes.apps.read_namespaced_stateful_set(
                name=self._names.statefulset, namespace=namespace
            )
            replicas = int(existing.spec.replicas or 0) if existing.spec else 1
        except client.ApiException as err:
            if err.status != 404:
                raise KubernetesError(
                    f"Unable to read StatefulSet {namespace}/{self._names.statefulset}: {err}"
                ) from err

        st = client.V1StatefulSet(
            metadata=client.V1ObjectMeta(
                name=self._names.statefulset,
                namespace=namespace,
                labels=labels,
            ),
            spec=client.V1StatefulSetSpec(
                replicas=replicas,
                selector=client.V1LabelSelector(match_labels=labels),
                service_name=self._names.headless_service,
                template=template,
            ),
        )

        try:
            await self.coresys.kubernetes.apps.create_namespaced_stateful_set(
                namespace=namespace, body=st
            )
        except client.ApiException as err:
            if err.status != 409:
                raise KubernetesError(
                    f"Unable to create StatefulSet {namespace}/{self._names.statefulset}: {err}"
                ) from err
            await self.coresys.kubernetes.apps.patch_namespaced_stateful_set(
                name=self._names.statefulset, namespace=namespace, body=st
            )

        await self._ensure_headless_service(labels)
        await self._ensure_service(labels)
        await self._refresh_cluster_ip()

        # If we changed configuration while Home Assistant was already running,
        # restart it so the reverse proxy settings take effect.
        if changed and await self.is_running():
            _LOGGER.info(
                "Restarting Home Assistant to apply reverse proxy configuration"
            )
            await self.restart()

    async def check_image(self, version: AwesomeVersion, image: str) -> None:
        """Ensure workload uses expected image.

        Implemented as an idempotent install/patch.
        """
        await self.install(version, image=image)

    async def update(self, version: AwesomeVersion, *, image: str) -> None:
        """Update the Home Assistant image."""
        await self.install(version, image=image)

    async def cleanup(self, *, old_image: str | None = None) -> None:
        """Cleanup old artifacts.

        No-op in Kubernetes.
        """
        return

    async def stop(self, *, remove_container: bool = True) -> None:
        """Stop Home Assistant (scale to 0)."""
        await self._scale(0)

    async def start(self) -> None:
        """Start Home Assistant (scale to 1) and wait Ready."""
        await self._scale(1)
        await self._wait_ready(timeout=STARTUP_TIMEOUT)

    async def restart(self) -> None:
        await self.stop(remove_container=False)
        await self.start()

    async def run(self, *, restore_job_id: str | None = None) -> None:
        """Create and start Home Assistant.

        The restore job id is not used in Kubernetes MVP.
        """
        if not self.coresys.homeassistant.version:
            raise HomeAssistantError("Home Assistant version is not set")

        await self.install(self.coresys.homeassistant.version, image=self.image)
        await self.start()

    async def is_initialize(self) -> bool:
        """Return True if the core workload is initialized."""
        return await self.exists()

    async def get_latest_version(self) -> AwesomeVersion:
        """Return best-known version."""
        if self.coresys.homeassistant.latest_version:
            return self.coresys.homeassistant.latest_version
        raise HomeAssistantError("Unable to determine latest Home Assistant version")

    async def stats(self):
        """Return resource stats.

        Not implemented for Kubernetes MVP.
        """
        return None

    async def is_failed(self) -> bool:
        """Return True if workload is in a failed state."""
        return False

    async def _scale(self, replicas: int) -> None:
        namespace = self.coresys.kubernetes.context.namespace
        body: dict[str, Any] = {"spec": {"replicas": replicas}}
        try:
            await self.coresys.kubernetes.apps.patch_namespaced_stateful_set_scale(
                name=self._names.statefulset, namespace=namespace, body=body
            )
        except client.ApiException as err:
            raise KubernetesError(
                f"Unable to scale StatefulSet {namespace}/{self._names.statefulset}: {err}"
            ) from err

    async def _wait_ready(self, *, timeout: int) -> None:
        end = asyncio.get_running_loop().time() + timeout
        while asyncio.get_running_loop().time() < end:
            if await self.is_running():
                return
            await asyncio.sleep(2)
        _LOGGER.warning("Timeout waiting for Home Assistant to become Ready")

    async def _ensure_service(self, selector_labels: dict[str, str]) -> None:
        namespace = self.coresys.kubernetes.context.namespace
        body = client.V1Service(
            metadata=client.V1ObjectMeta(name=self._names.service, namespace=namespace),
            spec=client.V1ServiceSpec(
                type="ClusterIP",
                selector=selector_labels,
                ports=[
                    client.V1ServicePort(
                        name="http",
                        port=8123,
                        target_port=8123,
                        protocol="TCP",
                    )
                ],
            ),
        )

        try:
            await self.coresys.kubernetes.core.create_namespaced_service(
                namespace=namespace, body=body
            )
        except client.ApiException as err:
            if err.status != 409:
                raise KubernetesError(
                    f"Unable to create Service {namespace}/{self._names.service}: {err}"
                ) from err
            await self.coresys.kubernetes.core.patch_namespaced_service(
                name=self._names.service, namespace=namespace, body=body
            )

    async def _ensure_headless_service(self, selector_labels: dict[str, str]) -> None:
        """Ensure the headless service exists for the StatefulSet."""
        namespace = self.coresys.kubernetes.context.namespace
        body = client.V1Service(
            metadata=client.V1ObjectMeta(
                name=self._names.headless_service, namespace=namespace
            ),
            spec=client.V1ServiceSpec(
                cluster_ip="None",
                publish_not_ready_addresses=True,
                selector=selector_labels,
                ports=[
                    client.V1ServicePort(
                        name="http",
                        port=8123,
                        target_port=8123,
                        protocol="TCP",
                    )
                ],
            ),
        )

        try:
            await self.coresys.kubernetes.core.create_namespaced_service(
                namespace=namespace, body=body
            )
        except client.ApiException as err:
            if err.status != 409:
                raise KubernetesError(
                    f"Unable to create Service {namespace}/{self._names.headless_service}: {err}"
                ) from err
            await self.coresys.kubernetes.core.patch_namespaced_service(
                name=self._names.headless_service, namespace=namespace, body=body
            )

    async def _refresh_cluster_ip(self) -> None:
        namespace = self.coresys.kubernetes.context.namespace
        try:
            svc = await self.coresys.kubernetes.core.read_namespaced_service(
                name=self._names.service, namespace=namespace
            )
        except client.ApiException as err:
            if err.status == 404:
                self._cluster_ip = IPv4Address("0.0.0.0")
                return
            raise KubernetesError(
                f"Unable to read Service {namespace}/{self._names.service}: {err}"
            ) from err

        ip = svc.spec.cluster_ip if svc.spec else None
        if not ip or ip == "None":
            self._cluster_ip = IPv4Address("0.0.0.0")
            return
        try:
            self._cluster_ip = IPv4Address(ip)
        except ValueError:
            self._cluster_ip = IPv4Address("0.0.0.0")

    def _trusted_proxies(self) -> list[str]:
        """Return list of trusted proxy CIDRs for Home Assistant.

        The Gateway/Envoy dataplane will add X-Forwarded-For. Home Assistant will
        reject such requests unless the source proxy address is trusted.
        """
        raw = os.environ.get(
            ENV_SUPERVISOR_K8S_HA_TRUSTED_PROXIES, DEFAULT_SUPERVISOR_K8S_HA_TRUSTED_PROXIES
        )
        proxies = [p.strip() for p in raw.split(",") if p.strip()]
        return proxies

    async def _ensure_reverse_proxy_config(self) -> bool:
        """Ensure Home Assistant is configured to accept reverse proxy headers.

        We do not parse YAML because Home Assistant configs often contain custom
        tags like `!include`. Instead, we append an `http:` section if one does
        not already exist.
        """
        config_file = self.coresys.config.path_homeassistant / "configuration.yaml"
        proxies = self._trusted_proxies()

        changed = False

        def _update_config() -> bool:
            if not config_file.exists():
                _LOGGER.info(
                    "Home Assistant configuration.yaml not found at %s; skipping reverse proxy configuration",
                    config_file,
                )
                return False

            try:
                content = config_file.read_text(encoding="utf-8")
            except OSError as err:
                _LOGGER.warning(
                    "Unable to read Home Assistant configuration.yaml at %s: %s",
                    config_file,
                    err,
                )
                return False

            if _RE_HTTP_SECTION.search(content):
                _LOGGER.debug(
                    "Home Assistant configuration already contains an http: section; skipping reverse proxy injection"
                )
                return False

            backup_file = config_file.with_name("configuration.yaml.supervisor.bak")
            if not backup_file.exists():
                try:
                    backup_file.write_text(content, encoding="utf-8")
                except OSError as err:
                    _LOGGER.debug("Unable to write config backup %s: %s", backup_file, err)

            trusted_lines = "\n".join(f"    - {proxy}" for proxy in proxies)
            block = (
                "\n\n# Managed by Supervisor (Kubernetes runtime): reverse proxy support\n"
                "http:\n"
                "  use_x_forwarded_for: true\n"
                "  trusted_proxies:\n"
                f"{trusted_lines}\n"
            )

            new_content = content.rstrip() + block
            try:
                with atomic_write(config_file, overwrite=True) as fp:
                    fp.write(new_content)
                config_file.chmod(0o600)
            except OSError as err:
                _LOGGER.warning(
                    "Unable to update Home Assistant configuration.yaml at %s: %s",
                    config_file,
                    err,
                )

                return False

            return True

        changed = await self.coresys.run_in_executor(_update_config)
        return bool(changed)


STARTUP_TIMEOUT = 15 * 60
