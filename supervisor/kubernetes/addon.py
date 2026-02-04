"""Kubernetes backend for Supervisor add-ons.

This implementation focuses on a safe, Kubernetes-native subset of add-ons:
- No host networking
- No device passthrough
- No privileged containers

It creates a Deployment + ClusterIP Service per add-on and mounts the shared
RWX PVC at /data using the existing Supervisor directory layout.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from ipaddress import IPv4Address
import logging
import re
from typing import TYPE_CHECKING, Any

from kubernetes_asyncio import client

from ..docker.const import ENV_TIME, ENV_TOKEN, ENV_TOKEN_OLD
from ..const import AddonState
from ..exceptions import AddonNotSupportedError, KubernetesError, KubernetesNotFound

if TYPE_CHECKING:
    from awesomeversion import AwesomeVersion

    from ..addons.addon import Addon
    from ..coresys import CoreSys


_LOGGER: logging.Logger = logging.getLogger(__name__)

_RE_INVALID_NAME: re.Pattern[str] = re.compile(r"[^a-z0-9-]+")


def _sanitize_k8s_name(name: str) -> str:
    """Sanitize a string for use as a Kubernetes resource name.

    We generate DNS-safe names for resources like Deployments/Services.
    """
    name = _RE_INVALID_NAME.sub("-", name.lower()).strip("-")
    name = re.sub(r"-+", "-", name)

    # Keep within the strictest common limit (DNS label)
    if len(name) > 63:
        name = name[:63].rstrip("-")

    return name or "addon"


@dataclass(slots=True, frozen=True)
class KubeAddonNames:
    """Kubernetes resource names for an add-on."""

    deployment: str
    service: str


class KubernetesAddon:
    """Kubernetes workload implementation for an add-on."""

    def __init__(self, coresys: CoreSys, addon: Addon) -> None:
        self.coresys = coresys
        self.addon = addon

        base_name = _sanitize_k8s_name(f"addon-{addon.slug}")
        self._names = KubeAddonNames(
            deployment=base_name,
            service=base_name,
        )
        self._cluster_ip: IPv4Address = IPv4Address("0.0.0.0")

    @property
    def name(self) -> str:
        return self._names.deployment

    @property
    def service_name(self) -> str:
        """Return Kubernetes Service name for this add-on."""
        return self._names.service

    @property
    def ip_address(self) -> IPv4Address:
        """Return a stable IP address to reach this add-on.

        We use the ClusterIP of the Service.
        """
        return self._cluster_ip

    async def ip_address_async(self) -> IPv4Address:
        """Async version of ip_address."""
        svc = await self._read_service()
        ip = svc.spec.cluster_ip if svc.spec else None
        if not ip or ip == "None":
            self._cluster_ip = IPv4Address("0.0.0.0")
            return self._cluster_ip
        try:
            self._cluster_ip = IPv4Address(ip)
            return self._cluster_ip
        except ValueError:
            self._cluster_ip = IPv4Address("0.0.0.0")
            return self._cluster_ip

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return False

    def _validate_supported(self) -> None:
        """Validate this add-on can run in the Kubernetes backend."""
        # Keep this intentionally strict for MVP.
        if self.addon.host_network:
            raise AddonNotSupportedError()
        if self.addon.with_full_access and not self.addon.protected:
            raise AddonNotSupportedError()
        if self.addon.devices or self.addon.static_devices:
            raise AddonNotSupportedError()
        if self.addon.with_gpio or self.addon.with_usb or self.addon.with_uart:
            raise AddonNotSupportedError()
        if self.addon.with_video:
            raise AddonNotSupportedError()

    async def exists(self) -> bool:
        """Return True if add-on Deployment exists."""
        try:
            await self.coresys.kubernetes.apps.read_namespaced_deployment(
                name=self._names.deployment,
                namespace=self.coresys.kubernetes.context.namespace,
            )
        except client.ApiException as err:
            if err.status == 404:
                return False
            raise KubernetesError(f"Unable to read Deployment {self.name}: {err}") from err
        return True

    async def install(
        self, version: AwesomeVersion, image: str | None, *, arch: str | None = None
    ) -> None:
        """Create or update the add-on Deployment/Service."""
        self._validate_supported()

        if not image:
            # Image build flow is not supported in Kubernetes MVP.
            raise AddonNotSupportedError()

        full_image = f"{image}:{version}"
        namespace = self.coresys.kubernetes.context.namespace
        labels = {
            "io.hass.type": "addon",
            "io.hass.addon": self.addon.slug,
            "io.hass.managed": "true",
        }

        env = [
            client.V1EnvVar(name=ENV_TIME, value=self.coresys.timezone),
            client.V1EnvVar(name=ENV_TOKEN, value=self.addon.supervisor_token),
            client.V1EnvVar(name=ENV_TOKEN_OLD, value=self.addon.supervisor_token),
        ]
        for key, value in (self.addon.environment or {}).items():
            env.append(client.V1EnvVar(name=key, value=str(value) if value is not None else ""))

        volume_name = "hassio-data"
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
                mount_path="/data",
                sub_path=f"addons/data/{self.addon.slug}",
            )
        ]

        # Many add-ons expect the Home Assistant config directory to be available at
        # /homeassistant (Docker-era convention). Mount the shared PVC subPath there.
        volume_mounts.append(
            client.V1VolumeMount(
                name=volume_name,
                mount_path="/homeassistant",
                sub_path="homeassistant",
            )
        )

        container_ports: list[client.V1ContainerPort] = []
        if self.addon.ingress_port:
            container_ports.append(client.V1ContainerPort(container_port=self.addon.ingress_port))
        # Also include declared ports so Services can target them.
        for port in (self.addon.ports or {}).keys():
            try:
                container_port = int(str(port).split("/")[0])
            except ValueError:
                continue
            if container_port not in {p.container_port for p in container_ports}:
                container_ports.append(client.V1ContainerPort(container_port=container_port))

        pod_template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels=labels),
            spec=client.V1PodSpec(
                containers=[
                    client.V1Container(
                        name="addon",
                        image=full_image,
                        env=env,
                        volume_mounts=volume_mounts,
                        ports=container_ports or None,
                    )
                ],
                volumes=volumes,
            ),
        )

        # Preserve current replica count if a Deployment already exists.
        replicas = 0
        try:
            existing = await self.coresys.kubernetes.apps.read_namespaced_deployment(
                name=self._names.deployment,
                namespace=namespace,
            )
            replicas = int(existing.spec.replicas or 0) if existing.spec else 0
        except client.ApiException as err:
            if err.status != 404:
                raise KubernetesError(
                    f"Unable to read Deployment {namespace}/{self._names.deployment}: {err}"
                ) from err

        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(
                name=self._names.deployment,
                namespace=namespace,
                labels=labels,
            ),
            spec=client.V1DeploymentSpec(
                replicas=replicas,
                selector=client.V1LabelSelector(match_labels=labels),
                template=pod_template,
            ),
        )

        try:
            await self.coresys.kubernetes.apps.create_namespaced_deployment(
                namespace=namespace, body=deployment
            )
        except client.ApiException as err:
            if err.status != 409:
                raise KubernetesError(
                    f"Unable to create Deployment {namespace}/{self._names.deployment}: {err}"
                ) from err
            await self.coresys.kubernetes.apps.patch_namespaced_deployment(
                name=self._names.deployment, namespace=namespace, body=deployment
            )

        await self._ensure_service(labels)

        # Refresh cached IP
        try:
            await self.ip_address_async()
        except KubernetesError:
            pass

    async def remove(self, *, remove_image: bool = True) -> None:
        """Remove Deployment and Service."""
        namespace = self.coresys.kubernetes.context.namespace
        try:
            await self.coresys.kubernetes.apps.delete_namespaced_deployment(
                name=self._names.deployment, namespace=namespace
            )
        except client.ApiException as err:
            if err.status != 404:
                raise KubernetesError(
                    f"Unable to delete Deployment {namespace}/{self._names.deployment}: {err}"
                ) from err

        try:
            await self.coresys.kubernetes.core.delete_namespaced_service(
                name=self._names.service, namespace=namespace
            )
        except client.ApiException as err:
            if err.status != 404:
                raise KubernetesError(
                    f"Unable to delete Service {namespace}/{self._names.service}: {err}"
                ) from err

    async def run(self) -> None:
        """Start the add-on (scale to 1) and wait for readiness."""
        self._validate_supported()

        if not await self.exists():
            raise KubernetesNotFound(f"Add-on {self.addon.slug} not installed")

        # Ensure the workload template includes the latest token before scaling.
        # In Kubernetes, scaling does not update the pod template.
        if self.addon.version and self.addon.image:
            await self.install(self.addon.version, self.addon.image, arch=self.addon.arch)

        await self._scale(1)
        await self._wait_ready(timeout=120)

    async def stop(self) -> None:
        """Stop the add-on (scale to 0)."""
        if not await self.exists():
            raise KubernetesNotFound(f"Add-on {self.addon.slug} not installed")
        await self._scale(0)
        await self._wait_stopped(timeout=60)

    async def get_state(self) -> AddonState:
        """Return add-on state based on Kubernetes resources."""
        if not await self.exists():
            return AddonState.STOPPED

        namespace = self.coresys.kubernetes.context.namespace
        labels = f"io.hass.type=addon,io.hass.addon={self.addon.slug},io.hass.managed=true"

        # If the workload is scaled down, treat as stopped.
        try:
            deployment = await self.coresys.kubernetes.apps.read_namespaced_deployment(
                name=self._names.deployment, namespace=namespace
            )
            if deployment.spec and (deployment.spec.replicas or 0) == 0:
                return AddonState.STOPPED
        except client.ApiException as err:
            if err.status != 404:
                raise KubernetesError(
                    f"Unable to read Deployment {namespace}/{self._names.deployment}: {err}"
                ) from err
            return AddonState.STOPPED

        pods = await self.coresys.kubernetes.core.list_namespaced_pod(
            namespace=namespace, label_selector=labels
        )

        # Ready => started
        for pod in pods.items:
            for cond in pod.status.conditions or []:
                if cond.type == "Ready" and cond.status == "True":
                    return AddonState.STARTED

        # Detect obvious failure states (CrashLoopBackOff, ImagePullBackOff, etc.)
        for pod in pods.items:
            for cs in pod.status.container_statuses or []:
                if cs.state and cs.state.waiting and cs.state.waiting.reason:
                    reason = cs.state.waiting.reason
                    if reason in {
                        "CrashLoopBackOff",
                        "ImagePullBackOff",
                        "ErrImagePull",
                        "CreateContainerConfigError",
                        "CreateContainerError",
                    }:
                        return AddonState.ERROR

        # Otherwise it exists and is scaled up but not ready yet.
        return AddonState.STARTUP

    async def restart(self) -> None:
        """Restart the add-on."""
        await self.stop()
        await self.run()

    async def is_running(self) -> bool:
        """Return True if the add-on pod is ready."""
        namespace = self.coresys.kubernetes.context.namespace
        labels = f"io.hass.type=addon,io.hass.addon={self.addon.slug},io.hass.managed=true"
        pods = await self.coresys.kubernetes.core.list_namespaced_pod(
            namespace=namespace, label_selector=labels
        )
        for pod in pods.items:
            for cond in pod.status.conditions or []:
                if cond.type == "Ready" and cond.status == "True":
                    return True
        return False

    async def attach(self, *, version: AwesomeVersion) -> None:
        """Attach to existing resources.

        For Kubernetes we don't maintain a separate attach step; exists() covers it.
        """
        if not await self.exists():
            raise KubernetesNotFound(f"Add-on {self.addon.slug} is not installed")

        # Refresh cached IP if service exists
        try:
            await self.ip_address_async()
        except KubernetesError:
            pass

    async def check_image(self, version: AwesomeVersion, image: str | None, arch: str) -> None:
        """Ensure workload uses expected image.

        This is implemented as an idempotent install/patch.
        """
        await self.install(version, image, arch=arch)

    async def update(
        self, version: AwesomeVersion, image: str | None, *, arch: str | None = None
    ) -> None:
        """Update add-on image/version."""
        await self.install(version, image, arch=arch)

    async def cleanup(
        self,
        *,
        old_image: str | None = None,
        image: str | None = None,
        version: AwesomeVersion | None = None,
    ) -> None:
        """Cleanup old artifacts.

        No-op on Kubernetes MVP.
        """
        return

    async def _scale(self, replicas: int) -> None:
        namespace = self.coresys.kubernetes.context.namespace
        body = {"spec": {"replicas": replicas}}
        try:
            await self.coresys.kubernetes.apps.patch_namespaced_deployment_scale(
                name=self._names.deployment, namespace=namespace, body=body
            )
        except client.ApiException as err:
            raise KubernetesError(
                f"Unable to scale Deployment {namespace}/{self._names.deployment}: {err}"
            ) from err

    async def _wait_ready(self, *, timeout: int) -> None:
        end = asyncio.get_running_loop().time() + timeout
        while asyncio.get_running_loop().time() < end:
            if await self.is_running():
                return
            await asyncio.sleep(1)
        raise KubernetesError(
            f"Timeout waiting for add-on {self.addon.slug} to become Ready"
        )

    async def _wait_stopped(self, *, timeout: int) -> None:
        """Wait for add-on pods to stop after scaling down."""
        end = asyncio.get_running_loop().time() + timeout
        namespace = self.coresys.kubernetes.context.namespace
        labels = f"io.hass.type=addon,io.hass.addon={self.addon.slug},io.hass.managed=true"
        while asyncio.get_running_loop().time() < end:
            pods = await self.coresys.kubernetes.core.list_namespaced_pod(
                namespace=namespace, label_selector=labels
            )
            if not pods.items:
                return
            await asyncio.sleep(1)
        raise KubernetesError(f"Timeout waiting for add-on {self.addon.slug} to stop")

    async def _ensure_service(self, selector_labels: dict[str, str]) -> None:
        namespace = self.coresys.kubernetes.context.namespace

        ports: list[client.V1ServicePort] = []
        # Expose ingress port for Supervisor proxy
        if self.addon.ingress_port:
            ports.append(
                client.V1ServicePort(
                    name="ingress",
                    port=self.addon.ingress_port,
                    target_port=self.addon.ingress_port,
                    protocol="TCP",
                )
            )

        # Expose declared ports for non-HTTP access (L4 routing)
        for container_port, host_port in (self.addon.ports or {}).items():
            if host_port is None:
                continue
            proto = "TCP"
            port_str = str(container_port)
            if "/" in port_str:
                port_part, proto_part = port_str.split("/", 1)
                proto = proto_part.upper()
            else:
                port_part = port_str
            try:
                port_num = int(port_part)
            except ValueError:
                continue
            ports.append(
                client.V1ServicePort(
                    name=f"p{port_num}-{proto.lower()}",
                    port=port_num,
                    target_port=port_num,
                    protocol=proto,
                )
            )

        if not ports:
            # Create a service with no ports is invalid; skip.
            return

        body = client.V1Service(
            metadata=client.V1ObjectMeta(name=self._names.service, namespace=namespace),
            spec=client.V1ServiceSpec(
                type="ClusterIP",
                selector=selector_labels,
                ports=ports,
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

    async def _read_service(self) -> client.V1Service:
        namespace = self.coresys.kubernetes.context.namespace
        try:
            return await self.coresys.kubernetes.core.read_namespaced_service(
                name=self._names.service, namespace=namespace
            )
        except client.ApiException as err:
            if err.status == 404:
                raise KubernetesNotFound(
                    f"Service {namespace}/{self._names.service} not found"
                ) from None
            raise KubernetesError(
                f"Unable to read Service {namespace}/{self._names.service}: {err}"
            ) from err
