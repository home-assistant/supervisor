"""Manager for Supervisor Kubernetes.

This is an early implementation scaffold used by the Kubernetes runtime backend.
The initial goal is to provide:
- Kubernetes API client initialization
- Namespace detection
- A small set of helpers for CRUD + observation

Resource modeling (Deployments/StatefulSets/Gateway API objects, etc.) will be
added incrementally.
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Self

from kubernetes_asyncio import client, config

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import KubernetesError
from .const import (
    ENV_SUPERVISOR_K8S_INTERNAL_GATEWAY_ADDRESS,
    ENV_SUPERVISOR_K8S_INTERNAL_GATEWAY_CLASS,
    ENV_SUPERVISOR_K8S_INTERNAL_GATEWAY_NAME,
    ENV_SUPERVISOR_K8S_GATEWAY_CLASS,
    ENV_SUPERVISOR_K8S_GATEWAY_HOSTNAME,
    ENV_SUPERVISOR_K8S_GATEWAY_NAME,
    ENV_SUPERVISOR_K8S_GATEWAY_TLS_SECRET,
    ENV_SUPERVISOR_K8S_HTTPROUTE_NAME,
    ENV_SUPERVISOR_K8S_MANAGE_PUBLIC_GATEWAY,
    ENV_SUPERVISOR_K8S_PORT_REGISTRY_CONFIGMAP,
    ENV_SUPERVISOR_K8S_PORT_REGISTRY_KEY,
    ENV_SUPERVISOR_K8S_SERVICE_HOMEASSISTANT,
    ENV_SUPERVISOR_K8S_SERVICE_HOMEASSISTANT_PORT,
    ENV_SUPERVISOR_K8S_SERVICE_SUPERVISOR,
    ENV_SUPERVISOR_K8S_SERVICE_SUPERVISOR_PORT,
    ENV_SUPERVISOR_K8S_KUBECONFIG,
    ENV_SUPERVISOR_K8S_NAMESPACE,
    ENV_SUPERVISOR_K8S_SHARED_PVC_CLAIM,
    ENV_SUPERVISOR_K8S_SHARED_PVC_SIZE,
    ENV_SUPERVISOR_K8S_SHARED_PVC_STORAGE_CLASS,
    ENV_SUPERVISOR_K8S_STORAGE_MODE,
    GATEWAY_API_GROUP,
    GATEWAY_API_VERSION,
    K8S_ANNOTATION_CILIUM_LB_IPAM_IPS,
    K8S_LABEL_MANAGED,
    K8S_NAMESPACE_FILE,
    K8S_STORAGE_MODE_SHARED_PVC,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)

_INTERNAL_L4_CONFIG_KEY = "nginx.conf"


@dataclass(slots=True, frozen=True)
class KubernetesContext:
    """Resolved Kubernetes runtime context."""

    namespace: str

    # Public (WAN) gateway, optional if GitOps-managed.
    manage_public_gateway: bool
    gateway_hostname: str | None
    gateway_tls_secret: str | None
    gateway_class: str | None
    gateway_name: str | None
    httproute_name: str | None

    # Internal (LAN-only) gateway for add-on TCP/UDP ports.
    internal_gateway_address: str
    internal_gateway_class: str
    internal_gateway_name: str

    service_homeassistant: str
    service_homeassistant_port: int
    service_supervisor: str
    service_supervisor_port: int

    shared_pvc_claim: str
    shared_pvc_storage_class: str
    shared_pvc_size: str

    port_registry_configmap: str
    port_registry_key: str


class KubernetesAPI(CoreSysAttributes):
    """Kubernetes API wrapper.

    This wrapper is intended to be AsyncIO-safe.
    """

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize Kubernetes base wrapper."""
        self.coresys = coresys
        self._context: KubernetesContext | None = None

        # API clients. These are created once config is loaded.
        self._core: client.CoreV1Api | None = None
        self._apps: client.AppsV1Api | None = None
        self._custom: client.CustomObjectsApi | None = None

    async def post_init(self) -> Self:
        """Initialize Kubernetes API clients."""
        await self._load_kube_config()

        namespace = self._detect_namespace()
        runtime = self._read_required_runtime_settings()
        self._context = KubernetesContext(namespace=namespace, **runtime)
        self._core = client.CoreV1Api()
        self._apps = client.AppsV1Api()
        self._custom = client.CustomObjectsApi()

        await self._ensure_storage()
        if self.context.manage_public_gateway:
            await self.ensure_gateway_http_routing()
        return self

    @property
    def context(self) -> KubernetesContext:
        """Return Kubernetes runtime context."""
        if self._context is None:
            raise RuntimeError("Kubernetes context not initialized")
        return self._context

    @property
    def core(self) -> client.CoreV1Api:
        """Return CoreV1 API."""
        if self._core is None:
            raise RuntimeError("Kubernetes client not initialized")
        return self._core

    @property
    def apps(self) -> client.AppsV1Api:
        """Return AppsV1 API."""
        if self._apps is None:
            raise RuntimeError("Kubernetes client not initialized")
        return self._apps

    @property
    def custom(self) -> client.CustomObjectsApi:
        """Return CustomObjects API (for CRDs like Gateway API)."""
        if self._custom is None:
            raise RuntimeError("Kubernetes client not initialized")
        return self._custom

    async def _load_kube_config(self) -> None:
        """Load Kubernetes configuration.

        Prefers in-cluster configuration. Falls back to kubeconfig for local dev.
        """
        try:
            # kubernetes-asyncio uses a synchronous in-cluster config loader.
            config.load_incluster_config()
            _LOGGER.debug("Loaded in-cluster Kubernetes configuration")
            return
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("In-cluster config not available: %s", err)

        kubeconfig = os.environ.get(ENV_SUPERVISOR_K8S_KUBECONFIG) or os.environ.get("KUBECONFIG")
        try:
            await config.load_kube_config(config_file=kubeconfig)
            _LOGGER.debug("Loaded kubeconfig Kubernetes configuration")
        except Exception as err:  # noqa: BLE001
            raise KubernetesError(f"Unable to load Kubernetes configuration: {err}") from err

    def _read_required_runtime_settings(self) -> dict[str, Any]:
        """Read and validate required Kubernetes runtime settings.

        Installer is responsible for providing all required values.
        """
        storage_mode = os.environ.get(ENV_SUPERVISOR_K8S_STORAGE_MODE)
        if storage_mode != K8S_STORAGE_MODE_SHARED_PVC:
            raise KubernetesError(
                f"Unsupported or missing {ENV_SUPERVISOR_K8S_STORAGE_MODE}. "
                f"Expected '{K8S_STORAGE_MODE_SHARED_PVC}'."
            )

        shared_pvc_claim = os.environ.get(ENV_SUPERVISOR_K8S_SHARED_PVC_CLAIM)
        shared_pvc_storage_class = os.environ.get(ENV_SUPERVISOR_K8S_SHARED_PVC_STORAGE_CLASS)
        shared_pvc_size = os.environ.get(ENV_SUPERVISOR_K8S_SHARED_PVC_SIZE)

        manage_public_gateway = (
            os.environ.get(ENV_SUPERVISOR_K8S_MANAGE_PUBLIC_GATEWAY, "false").lower()
            in ("1", "true", "yes", "on")
        )

        gateway_hostname = os.environ.get(ENV_SUPERVISOR_K8S_GATEWAY_HOSTNAME)
        gateway_tls_secret = os.environ.get(ENV_SUPERVISOR_K8S_GATEWAY_TLS_SECRET)

        internal_gateway_address = os.environ.get(ENV_SUPERVISOR_K8S_INTERNAL_GATEWAY_ADDRESS)
        if not internal_gateway_address:
            raise KubernetesError(
                f"Missing required Kubernetes runtime environment variable: {ENV_SUPERVISOR_K8S_INTERNAL_GATEWAY_ADDRESS}"
            )

        missing = [
            key
            for key, value in (
                (ENV_SUPERVISOR_K8S_SHARED_PVC_CLAIM, shared_pvc_claim),
                (ENV_SUPERVISOR_K8S_SHARED_PVC_STORAGE_CLASS, shared_pvc_storage_class),
                (ENV_SUPERVISOR_K8S_SHARED_PVC_SIZE, shared_pvc_size),
            )
            if not value
        ]

        # Public gateway settings only required when Supervisor manages them.
        if manage_public_gateway:
            missing.extend(
                [
                    key
                    for key, value in (
                        (ENV_SUPERVISOR_K8S_GATEWAY_HOSTNAME, gateway_hostname),
                        (ENV_SUPERVISOR_K8S_GATEWAY_TLS_SECRET, gateway_tls_secret),
                    )
                    if not value
                ]
            )
        if missing:
            raise KubernetesError(
                "Missing required Kubernetes runtime environment variables: "
                + ", ".join(missing)
            )

        # Service routing defaults. These will match whatever your installer deploys.
        # They are intentionally configurable to avoid coupling to any specific helm chart.
        service_homeassistant = (
            os.environ.get(ENV_SUPERVISOR_K8S_SERVICE_HOMEASSISTANT, "homeassistant")
            or "homeassistant"
        )
        service_supervisor = (
            os.environ.get(ENV_SUPERVISOR_K8S_SERVICE_SUPERVISOR, "supervisor")
            or "supervisor"
        )
        try:
            service_homeassistant_port = int(
                os.environ.get(ENV_SUPERVISOR_K8S_SERVICE_HOMEASSISTANT_PORT, "8123")
            )
            service_supervisor_port = int(
                os.environ.get(ENV_SUPERVISOR_K8S_SERVICE_SUPERVISOR_PORT, "80")
            )
        except ValueError as err:
            raise KubernetesError(f"Invalid service port configuration: {err}") from err

        return {
            "manage_public_gateway": manage_public_gateway,
            "gateway_hostname": gateway_hostname if manage_public_gateway else None,
            "gateway_tls_secret": gateway_tls_secret if manage_public_gateway else None,
            "gateway_class": (
                os.environ.get(ENV_SUPERVISOR_K8S_GATEWAY_CLASS, "cilium") or "cilium"
            )
            if manage_public_gateway
            else None,
            "gateway_name": (
                os.environ.get(ENV_SUPERVISOR_K8S_GATEWAY_NAME, "main-gateway")
                or "main-gateway"
            )
            if manage_public_gateway
            else None,
            "httproute_name": (
                os.environ.get(ENV_SUPERVISOR_K8S_HTTPROUTE_NAME, "ha-http") or "ha-http"
            )
            if manage_public_gateway
            else None,

            "internal_gateway_address": internal_gateway_address,
            "internal_gateway_class": (
                os.environ.get(ENV_SUPERVISOR_K8S_INTERNAL_GATEWAY_CLASS, "cilium")
                or "cilium"
            ),
            "internal_gateway_name": (
                os.environ.get(ENV_SUPERVISOR_K8S_INTERNAL_GATEWAY_NAME, "ha-internal")
                or "ha-internal"
            ),
            "service_homeassistant": service_homeassistant,
            "service_homeassistant_port": service_homeassistant_port,
            "service_supervisor": service_supervisor,
            "service_supervisor_port": service_supervisor_port,
            "shared_pvc_claim": shared_pvc_claim,
            "shared_pvc_storage_class": shared_pvc_storage_class,
            "shared_pvc_size": shared_pvc_size,
            "port_registry_configmap": os.environ.get(
                ENV_SUPERVISOR_K8S_PORT_REGISTRY_CONFIGMAP, "supervisor-port-registry"
            )
            or "supervisor-port-registry",
            "port_registry_key": os.environ.get(
                ENV_SUPERVISOR_K8S_PORT_REGISTRY_KEY, "registry.json"
            )
            or "registry.json",
        }

    def _detect_namespace(self) -> str:
        """Detect namespace Supervisor should operate in."""
        if (ns := os.environ.get(ENV_SUPERVISOR_K8S_NAMESPACE)):
            return ns

        ns_file = Path(K8S_NAMESPACE_FILE)
        if ns_file.exists():
            try:
                return ns_file.read_text(encoding="ascii").strip()
            except OSError as err:
                _LOGGER.debug("Failed reading namespace file %s: %s", ns_file, err)

        return "default"

    async def _ensure_storage(self) -> None:
        """Ensure storage prerequisites exist.

        For MVP we support a single shared RWX PVC.
        """
        await self._ensure_shared_pvc(
            claim_name=self.context.shared_pvc_claim,
            storage_class=self.context.shared_pvc_storage_class,
            size=self.context.shared_pvc_size,
        )

    async def ensure_gateway_http_routing(self) -> None:
        """Ensure Gateway + HTTPRoute exist for HA + Supervisor ingress.

        This sets up a single external IP (via Gateway) and routes:
        - / -> Home Assistant service
        - /api/hassio_ingress -> Supervisor service

        TLS is terminated at the Gateway using the installer-managed cert-manager Secret.
        """
        await self._ensure_gateway()
        await self._ensure_http_route()

    async def sync_addon_ports(
        self, *, addon_slug: str, service_name: str, ports: dict[str, int | None] | None
    ) -> None:
        """Sync L4 port exposure for an add-on.

        Ports is the Supervisor-style mapping of container ports (e.g. "1883/tcp")
        to external port numbers. For Kubernetes we interpret a non-null external
        port as "expose this port on the shared Gateway IP".
        """
        desired: list[tuple[int, str, int]] = []
        for container_port, external_port in (ports or {}).items():
            if external_port is None:
                continue
            proto = "tcp"
            port_str = str(container_port)
            if "/" in port_str:
                port_part, proto_part = port_str.split("/", 1)
                proto = proto_part.lower()
            else:
                port_part = port_str
            try:
                container_port_num = int(port_part)
                external_port_num = int(external_port)
            except (TypeError, ValueError):
                continue

            if proto not in ("tcp", "udp"):
                continue
            desired.append((container_port_num, proto, external_port_num))

        registry = await self._read_port_registry()

        # Remove previous entries owned by this addon
        registry = {
            k: v for k, v in registry.items() if v.get("addon") != addon_slug
        }

        # Add desired entries, detecting conflicts
        for container_port_num, proto, external_port_num in desired:
            key = f"{external_port_num}/{proto}"
            if key in registry:
                raise KubernetesError(
                    f"Port already claimed: {key} by {registry[key].get('addon')}"
                )
            registry[key] = {
                "addon": addon_slug,
                "service": service_name,
                "targetPort": container_port_num,
                "protocol": proto,
            }

        await self._write_port_registry(registry)

        # Program internal (LAN-only) L4 exposure using a dedicated LoadBalancer
        # service and an in-cluster TCP proxy. This avoids relying on TCPRoute/
        # UDPRoute support in the gateway controller.
        await self._ensure_internal_l4_proxy(registry)

    async def remove_addon_ports(self, *, addon_slug: str) -> None:
        """Remove all exposed ports for an add-on."""
        registry = await self._read_port_registry()
        changed = False
        for key in list(registry):
            if registry[key].get("addon") == addon_slug:
                registry.pop(key)
                changed = True
        if not changed:
            return
        await self._write_port_registry(registry)

        await self._ensure_internal_l4_proxy(registry)

    async def reconcile_addon_ports(self) -> None:
        """Reconcile internal L4 exposure based on the persisted registry.

        This is used on Supervisor startup in Kubernetes runtime to recreate the
        internal LoadBalancer + proxy stack after a restart.
        """
        registry = await self._read_port_registry()
        await self._ensure_internal_l4_proxy(registry)

    async def _read_port_registry(self) -> dict[str, dict[str, Any]]:
        name = self.context.port_registry_configmap
        namespace = self.context.namespace
        try:
            cm = await self.core.read_namespaced_config_map(name=name, namespace=namespace)
        except client.ApiException as err:
            if err.status != 404:
                raise KubernetesError(
                    f"Unable to read ConfigMap {namespace}/{name}: {err}"
                ) from err
            cm = None

        if cm is None or not cm.data or self.context.port_registry_key not in cm.data:
            return {}

        try:
            raw = cm.data[self.context.port_registry_key]
            return json.loads(raw) if raw else {}
        except Exception as err:  # noqa: BLE001
            raise KubernetesError(
                f"Invalid port registry data in {namespace}/{name}: {err}"
            ) from err

    async def _write_port_registry(self, registry: dict[str, dict[str, Any]]) -> None:
        name = self.context.port_registry_configmap
        payload = json.dumps(registry, sort_keys=True)
        await self.ensure_configmap(name, data={self.context.port_registry_key: payload})

    async def _ensure_internal_gateway_l4_listeners(
        self, registry: dict[str, dict[str, Any]]
    ) -> None:
        """Ensure internal Gateway listeners include all exposed TCP/UDP ports."""
        # If no ports are exposed, remove the internal gateway to avoid leaving
        # stale listeners open.
        if not registry:
            await self.delete_custom_object(
                group=GATEWAY_API_GROUP,
                version=GATEWAY_API_VERSION,
                plural="gateways",
                name=self.context.internal_gateway_name,
            )
            return

        listeners: list[dict[str, Any]] = []

        # L4 listeners
        for key in sorted(registry):
            external, proto = key.split("/", 1)
            port_num = int(external)
            proto_upper = proto.upper()
            listeners.append(
                {
                    "name": f"{proto}-{port_num}",
                    "port": port_num,
                    "protocol": proto_upper,
                    "allowedRoutes": {"namespaces": {"from": "Same"}},
                }
            )

        body: dict[str, Any] = {
            "apiVersion": f"{GATEWAY_API_GROUP}/{GATEWAY_API_VERSION}",
            "kind": "Gateway",
            "metadata": {
                "name": self.context.internal_gateway_name,
                "namespace": self.context.namespace,
                "labels": {K8S_LABEL_MANAGED: "true"},
            },
            "spec": {
                "gatewayClassName": self.context.internal_gateway_class,
                "addresses": [
                    {"type": "IPAddress", "value": self.context.internal_gateway_address}
                ],
                "listeners": listeners,
            },
        }

        await self.ensure_custom_object(
            group=GATEWAY_API_GROUP,
            version=GATEWAY_API_VERSION,
            plural="gateways",
            name=self.context.internal_gateway_name,
            body=body,
        )

    async def _ensure_internal_l4_proxy(self, registry: dict[str, dict[str, Any]]) -> None:
        """Ensure internal-only L4 proxy exists for exposed add-on ports.

        This creates:
        - ConfigMap with an NGINX stream configuration
        - Deployment running NGINX as a TCP/UDP proxy
        - Service type LoadBalancer bound to the configured internal VIP
        """
        name = self.context.internal_gateway_name
        namespace = self.context.namespace
        labels = {K8S_LABEL_MANAGED: "true", "io.hass.component": "internal-l4"}

        # Determine desired ports
        entries: list[tuple[int, str, str, int, str]] = []
        for key, entry in registry.items():
            external, proto = key.split("/", 1)
            if proto not in ("tcp", "udp"):
                continue
            entries.append(
                (
                    int(external),
                    proto,
                    entry["service"],
                    int(entry["targetPort"]),
                    entry.get("addon") or "unknown",
                )
            )

        # Always clean up managed Gateway API L4 objects; we no longer rely on
        # TCPRoute/UDPRoute for port exposure.
        await self._cleanup_gateway_api_l4_objects()

        # If nothing is exposed, clean up any existing proxy resources
        if not entries:
            await self._delete_internal_l4_proxy(name=name)
            return

        nginx_cfg = self._render_nginx_stream_cfg(namespace=namespace, entries=entries)
        cfg_hash = hashlib.sha256(nginx_cfg.encode("utf-8")).hexdigest()[:12]

        # ConfigMap
        await self.ensure_configmap(
            f"{name}-config",
            data={_INTERNAL_L4_CONFIG_KEY: nginx_cfg},
            labels=labels,
        )

        # Deployment
        await self._ensure_internal_l4_deployment(
            name=name,
            namespace=namespace,
            labels=labels,
            config_hash=cfg_hash,
        )

        # Service
        await self._ensure_internal_l4_service(
            name=name,
            namespace=namespace,
            labels=labels,
            ports=[(port, proto) for port, proto, *_ in entries],
        )

    async def _delete_internal_l4_proxy(self, *, name: str) -> None:
        namespace = self.context.namespace
        with contextlib.suppress(client.ApiException):
            await self.apps.delete_namespaced_deployment(name=name, namespace=namespace)
        with contextlib.suppress(client.ApiException):
            await self.core.delete_namespaced_service(name=name, namespace=namespace)
        with contextlib.suppress(client.ApiException):
            await self.core.delete_namespaced_config_map(
                name=f"{name}-config", namespace=namespace
            )

    async def _cleanup_gateway_api_l4_objects(self) -> None:
        """Remove managed Gateway API L4 resources (TCPRoute/UDPRoute/Gateway).

        Clusters differ in Gateway API L4 support; if the CRDs are not installed,
        the API will return 404. We ignore those cases.
        """

        # Internal Gateway object used by the old implementation
        await self.delete_custom_object(
            group=GATEWAY_API_GROUP,
            version=GATEWAY_API_VERSION,
            plural="gateways",
            name=self.context.internal_gateway_name,
        )

        namespace = self.context.namespace
        for plural in ("tcproutes", "udproutes"):
            try:
                obj = await self.custom.list_namespaced_custom_object(
                    group=GATEWAY_API_GROUP,
                    version=GATEWAY_API_VERSION,
                    namespace=namespace,
                    plural=plural,
                )
            except client.ApiException as err:
                if err.status == 404:
                    continue
                raise KubernetesError(
                    f"Unable to list {GATEWAY_API_GROUP}/{GATEWAY_API_VERSION} {plural} in {namespace}: {err}"
                ) from err

            for item in obj.get("items", []):
                labels = (item.get("metadata") or {}).get("labels") or {}
                if labels.get(K8S_LABEL_MANAGED) != "true":
                    continue
                name = (item.get("metadata") or {}).get("name")
                if not name:
                    continue
                await self.delete_custom_object(
                    group=GATEWAY_API_GROUP,
                    version=GATEWAY_API_VERSION,
                    plural=plural,
                    name=name,
                )

    def _render_nginx_stream_cfg(
        self, *, namespace: str, entries: list[tuple[int, str, str, int, str]]
    ) -> str:
        """Render an NGINX stream config for TCP/UDP proxying.

        entries: (external_port, proto, service_name, target_port, addon_slug)
        """
        lines: list[str] = [
            "worker_processes  1;",
            "error_log  /var/log/nginx/error.log info;",
            "pid        /var/run/nginx.pid;",
            "",
            "events {",
            "  worker_connections  1024;",
            "}",
            "",
            "stream {",
            "  # L4 proxy managed by Home Assistant Supervisor",
            "  # NOTE: This uses Cluster DNS names for backends.",
            "  #       A rollout occurs when this file changes.",
            "",
        ]

        for external_port, proto, service_name, target_port, addon_slug in sorted(entries):
            svc_fqdn = f"{service_name}.{namespace}.svc.cluster.local"
            listen = f"  listen {external_port} {proto};" if proto == "udp" else f"  listen {external_port};"
            lines.extend(
                [
                    "  server {",
                    f"    # addon={addon_slug}",
                    listen,
                    "    proxy_connect_timeout 5s;",
                    "    proxy_timeout 1m;",
                    f"    proxy_pass {svc_fqdn}:{target_port};",
                    "  }",
                    "",
                ]
            )

        lines.append("}")
        return "\n".join(lines)

    async def _ensure_internal_l4_deployment(
        self,
        *,
        name: str,
        namespace: str,
        labels: dict[str, str],
        config_hash: str,
    ) -> None:
        image = os.environ.get(
            "SUPERVISOR_K8S_INTERNAL_L4_IMAGE", "nginx:1.25-alpine"
        )
        body = client.V1Deployment(
            metadata=client.V1ObjectMeta(name=name, namespace=namespace, labels=labels),
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(match_labels=labels),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels=labels,
                        annotations={"io.hass.config-hash": config_hash},
                    ),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name="l4-proxy",
                                image=image,
                                volume_mounts=[
                                    client.V1VolumeMount(
                                        name="config",
                                        mount_path="/etc/nginx/nginx.conf",
                                        sub_path=_INTERNAL_L4_CONFIG_KEY,
                                    )
                                ],
                            )
                        ],
                        volumes=[
                            client.V1Volume(
                                name="config",
                                config_map=client.V1ConfigMapVolumeSource(
                                    name=f"{name}-config"
                                ),
                            )
                        ],
                    ),
                ),
            ),
        )

        try:
            await self.apps.create_namespaced_deployment(namespace=namespace, body=body)
        except client.ApiException as err:
            if err.status != 409:
                raise KubernetesError(
                    f"Unable to create internal L4 deployment {namespace}/{name}: {err}"
                ) from err
            await self.apps.patch_namespaced_deployment(
                name=name, namespace=namespace, body=body
            )

    async def _ensure_internal_l4_service(
        self,
        *,
        name: str,
        namespace: str,
        labels: dict[str, str],
        ports: list[tuple[int, str]],
    ) -> None:
        svc_ports: list[client.V1ServicePort] = []
        for port, proto in sorted({(p, pr) for p, pr in ports}):
            svc_ports.append(
                client.V1ServicePort(
                    name=f"{proto}-{port}",
                    port=port,
                    target_port=port,
                    protocol=proto.upper(),
                )
            )

        # Provider-specific annotations for the internal LoadBalancer service.
        #
        # For example, on Cilium with LB IPAM enabled, you typically need
        # `io.cilium/lb-ipam-ips` for a deterministic VIP.
        annotations: dict[str, str] = {}

        raw_annotations = os.environ.get("SUPERVISOR_K8S_INTERNAL_L4_SERVICE_ANNOTATIONS")
        if raw_annotations:
            try:
                extra = json.loads(raw_annotations)
                if not isinstance(extra, dict):
                    raise TypeError("annotations must be a JSON object")
            except Exception as err:  # noqa: BLE001
                raise KubernetesError(
                    "Invalid SUPERVISOR_K8S_INTERNAL_L4_SERVICE_ANNOTATIONS; expected a JSON object"
                ) from err
            annotations.update({str(k): str(v) for k, v in extra.items()})

        if self.context.internal_gateway_class == "cilium":
            annotations.setdefault(
                K8S_ANNOTATION_CILIUM_LB_IPAM_IPS, self.context.internal_gateway_address
            )

        body = client.V1Service(
            metadata=client.V1ObjectMeta(
                name=name,
                namespace=namespace,
                labels=labels,
                annotations=annotations or None,
            ),
            spec=client.V1ServiceSpec(
                type="LoadBalancer",
                load_balancer_ip=self.context.internal_gateway_address,
                selector=labels,
                ports=svc_ports,
            ),
        )

        try:
            await self.core.create_namespaced_service(namespace=namespace, body=body)
        except client.ApiException as err:
            if err.status != 409:
                raise KubernetesError(
                    f"Unable to create internal L4 service {namespace}/{name}: {err}"
                ) from err
            await self.core.patch_namespaced_service(
                name=name, namespace=namespace, body=body
            )

    async def _ensure_l4_routes(self, registry: dict[str, dict[str, Any]]) -> None:
        """Ensure TCPRoute/UDPRoute objects exist for all registry entries."""
        desired_tcp: set[str] = set()
        desired_udp: set[str] = set()

        for key, entry in registry.items():
            external, proto = key.split("/", 1)
            external_port = int(external)
            listener_name = f"{proto}-{external_port}"
            addon_slug = entry["addon"]
            service = entry["service"]
            target_port = int(entry["targetPort"])

            route_kind = "TCPRoute" if proto == "tcp" else "UDPRoute"
            plural = "tcproutes" if proto == "tcp" else "udproutes"
            route_name = f"addon-{addon_slug}-{proto}-{external_port}"

            if proto == "tcp":
                desired_tcp.add(route_name)
            else:
                desired_udp.add(route_name)

            body: dict[str, Any] = {
                "apiVersion": f"{GATEWAY_API_GROUP}/{GATEWAY_API_VERSION}",
                "kind": route_kind,
                "metadata": {
                    "name": route_name,
                    "namespace": self.context.namespace,
                    "labels": {K8S_LABEL_MANAGED: "true"},
                },
                "spec": {
                    "parentRefs": [
                        {
                            "name": self.context.internal_gateway_name,
                            "sectionName": listener_name,
                        }
                    ],
                    "rules": [
                        {
                            "backendRefs": [
                                {"name": service, "port": target_port}
                            ]
                        }
                    ],
                },
            }

            await self.ensure_custom_object(
                group=GATEWAY_API_GROUP,
                version=GATEWAY_API_VERSION,
                plural=plural,
                name=route_name,
                body=body,
            )

        # Cleanup stale managed routes
        for plural, desired in (("tcproutes", desired_tcp), ("udproutes", desired_udp)):
            items = await self.list_custom_objects(
                group=GATEWAY_API_GROUP, version=GATEWAY_API_VERSION, plural=plural
            )
            for item in items:
                metadata = item.get("metadata", {})
                name = metadata.get("name")
                labels = metadata.get("labels", {})
                if labels.get(K8S_LABEL_MANAGED) != "true":
                    continue
                if name and name not in desired:
                    await self.delete_custom_object(
                        group=GATEWAY_API_GROUP,
                        version=GATEWAY_API_VERSION,
                        plural=plural,
                        name=name,
                    )

    async def _ensure_gateway(self) -> None:
        if not self.context.manage_public_gateway:
            return

        name = self.context.gateway_name
        if not name or not self.context.gateway_hostname or not self.context.gateway_tls_secret:
            raise KubernetesError("Public gateway configuration is missing")
        body: dict[str, Any] = {
            "apiVersion": f"{GATEWAY_API_GROUP}/{GATEWAY_API_VERSION}",
            "kind": "Gateway",
            "metadata": {
                "name": name,
                "namespace": self.context.namespace,
                "labels": {K8S_LABEL_MANAGED: "true"},
            },
            "spec": {
                "gatewayClassName": self.context.gateway_class,
                "listeners": [
                    {
                        "name": "https",
                        "hostname": self.context.gateway_hostname,
                        "port": 443,
                        "protocol": "HTTPS",
                        "tls": {
                            "mode": "Terminate",
                            "certificateRefs": [
                                {
                                    "kind": "Secret",
                                    "name": self.context.gateway_tls_secret,
                                }
                            ],
                        },
                        "allowedRoutes": {
                            "namespaces": {"from": "Same"},
                        },
                    }
                ],
            },
        }

        await self.ensure_custom_object(
            group=GATEWAY_API_GROUP,
            version=GATEWAY_API_VERSION,
            plural="gateways",
            name=name,
            body=body,
        )

    async def _ensure_http_route(self) -> None:
        if not self.context.manage_public_gateway:
            return

        name = self.context.httproute_name
        if (
            not name
            or not self.context.gateway_name
            or not self.context.gateway_hostname
        ):
            raise KubernetesError("Public HTTPRoute configuration is missing")
        body: dict[str, Any] = {
            "apiVersion": f"{GATEWAY_API_GROUP}/{GATEWAY_API_VERSION}",
            "kind": "HTTPRoute",
            "metadata": {
                "name": name,
                "namespace": self.context.namespace,
                "labels": {K8S_LABEL_MANAGED: "true"},
            },
            "spec": {
                "parentRefs": [{"name": self.context.gateway_name}],
                "hostnames": [self.context.gateway_hostname],
                "rules": [
                    {
                        "matches": [
                            {
                                "path": {
                                    "type": "PathPrefix",
                                    "value": "/api/hassio_ingress",
                                }
                            }
                        ],
                        "backendRefs": [
                            {
                                "name": self.context.service_supervisor,
                                "port": self.context.service_supervisor_port,
                            }
                        ],
                    },
                    {
                        "matches": [
                            {"path": {"type": "PathPrefix", "value": "/"}}
                        ],
                        "backendRefs": [
                            {
                                "name": self.context.service_homeassistant,
                                "port": self.context.service_homeassistant_port,
                            }
                        ],
                    },
                ],
            },
        }

        await self.ensure_custom_object(
            group=GATEWAY_API_GROUP,
            version=GATEWAY_API_VERSION,
            plural="httproutes",
            name=name,
            body=body,
        )

    async def _ensure_shared_pvc(self, *, claim_name: str, storage_class: str, size: str) -> None:
        """Ensure the shared PersistentVolumeClaim exists and matches expectations."""
        namespace = self.context.namespace
        try:
            pvc = await self.core.read_namespaced_persistent_volume_claim(
                name=claim_name, namespace=namespace
            )
        except client.ApiException as err:
            if err.status != 404:
                raise KubernetesError(
                    f"Unable to read PVC {namespace}/{claim_name}: {err}"
                ) from err
            pvc = None

        if pvc is None:
            _LOGGER.info(
                "Creating shared RWX PVC %s/%s (storageClass=%s, size=%s)",
                namespace,
                claim_name,
                storage_class,
                size,
            )
            body = client.V1PersistentVolumeClaim(
                metadata=client.V1ObjectMeta(name=claim_name, namespace=namespace),
                spec=client.V1PersistentVolumeClaimSpec(
                    access_modes=["ReadWriteMany"],
                    resources=client.V1ResourceRequirements(requests={"storage": size}),
                    storage_class_name=storage_class,
                ),
            )
            try:
                await self.core.create_namespaced_persistent_volume_claim(
                    namespace=namespace, body=body
                )
            except Exception as err:  # noqa: BLE001
                raise KubernetesError(
                    f"Unable to create PVC {namespace}/{claim_name}: {err}"
                ) from err
            return

        existing_sc = pvc.spec.storage_class_name if pvc.spec else None
        if existing_sc != storage_class:
            raise KubernetesError(
                f"PVC {namespace}/{claim_name} storageClass mismatch: "
                f"expected '{storage_class}', got '{existing_sc}'"
            )

        existing_modes = set(pvc.spec.access_modes or []) if pvc.spec else set()
        if "ReadWriteMany" not in existing_modes:
            raise KubernetesError(
                f"PVC {namespace}/{claim_name} accessModes mismatch: "
                f"expected to include ReadWriteMany, got {sorted(existing_modes)}"
            )

    async def get_pod_logs(self, name: str, *, tail: int = 100) -> str:
        """Fetch pod logs for a pod in the managed namespace."""
        try:
            return await self.core.read_namespaced_pod_log(
                name=name, namespace=self.context.namespace, tail_lines=tail
            )
        except Exception as err:  # noqa: BLE001
            raise KubernetesError(f"Unable to read logs for pod {name}: {err}") from err

    async def list_pods(self, *, label_selector: str | None = None) -> list[client.V1Pod]:
        """List pods in the managed namespace."""
        try:
            pods = await self.core.list_namespaced_pod(
                namespace=self.context.namespace, label_selector=label_selector
            )
            return pods.items
        except Exception as err:  # noqa: BLE001
            raise KubernetesError(f"Unable to list pods: {err}") from err

    async def ensure_configmap(
        self,
        name: str,
        *,
        data: dict[str, str],
        labels: dict[str, str] | None = None,
        annotations: dict[str, str] | None = None,
    ) -> None:
        """Create or patch a ConfigMap in the managed namespace."""
        body = client.V1ConfigMap(
            metadata=client.V1ObjectMeta(
                name=name,
                namespace=self.context.namespace,
                labels=labels,
                annotations=annotations,
            ),
            data=data,
        )

        try:
            await self.core.create_namespaced_config_map(
                namespace=self.context.namespace, body=body
            )
            return
        except client.ApiException as err:
            if err.status != 409:
                raise KubernetesError(f"Unable to create ConfigMap {name}: {err}") from err

        # Exists -> patch
        try:
            await self.core.patch_namespaced_config_map(
                name=name, namespace=self.context.namespace, body=body
            )
        except Exception as err:  # noqa: BLE001
            raise KubernetesError(f"Unable to patch ConfigMap {name}: {err}") from err

    async def ensure_secret(
        self,
        name: str,
        *,
        string_data: dict[str, str],
        labels: dict[str, str] | None = None,
        annotations: dict[str, str] | None = None,
        secret_type: str | None = None,
    ) -> None:
        """Create or patch a Secret in the managed namespace."""
        body = client.V1Secret(
            metadata=client.V1ObjectMeta(
                name=name,
                namespace=self.context.namespace,
                labels=labels,
                annotations=annotations,
            ),
            type=secret_type,
            string_data=string_data,
        )

        try:
            await self.core.create_namespaced_secret(namespace=self.context.namespace, body=body)
            return
        except client.ApiException as err:
            if err.status != 409:
                raise KubernetesError(f"Unable to create Secret {name}: {err}") from err

        try:
            await self.core.patch_namespaced_secret(
                name=name, namespace=self.context.namespace, body=body
            )
        except Exception as err:  # noqa: BLE001
            raise KubernetesError(f"Unable to patch Secret {name}: {err}") from err

    async def ensure_custom_object(
        self,
        *,
        group: str,
        version: str,
        plural: str,
        name: str,
        body: dict[str, Any],
    ) -> None:
        """Create or patch a namespaced custom object.

        Used for Gateway API objects when not available as first-class models.
        """
        namespace = self.context.namespace
        try:
            await self.custom.create_namespaced_custom_object(
                group=group, version=version, namespace=namespace, plural=plural, body=body
            )
            return
        except client.ApiException as err:
            if err.status != 409:
                raise KubernetesError(
                    f"Unable to create {group}/{version} {plural}/{name}: {err}"
                ) from err

        try:
            await self.custom.patch_namespaced_custom_object(
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
                name=name,
                body=body,
                _content_type="application/merge-patch+json",
            )
        except Exception as err:  # noqa: BLE001
            raise KubernetesError(
                f"Unable to patch {group}/{version} {plural}/{name}: {err}"
            ) from err

    async def delete_custom_object(
        self, *, group: str, version: str, plural: str, name: str
    ) -> None:
        """Delete a namespaced custom object if it exists."""
        namespace = self.context.namespace
        try:
            await self.custom.delete_namespaced_custom_object(
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
                name=name,
            )
        except client.ApiException as err:
            if err.status != 404:
                raise KubernetesError(
                    f"Unable to delete {group}/{version} {plural}/{name}: {err}"
                ) from err

    async def list_custom_objects(
        self, *, group: str, version: str, plural: str
    ) -> list[dict[str, Any]]:
        """List namespaced custom objects."""
        namespace = self.context.namespace
        try:
            obj = await self.custom.list_namespaced_custom_object(
                group=group, version=version, namespace=namespace, plural=plural
            )
        except Exception as err:  # noqa: BLE001
            raise KubernetesError(
                f"Unable to list {group}/{version} {plural} in {namespace}: {err}"
            ) from err
        return obj.get("items", [])
