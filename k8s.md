Kubernetes Runtime (Supervisor)
==============================

This repository contains an experimental Kubernetes runtime backend for Home Assistant
Supervisor. The goal is to run Supervisor + Home Assistant Core + add-ons on a Kubernetes
cluster (instead of Docker-on-host) while preserving the Supervisor API contract that Home
Assistant uses.

High-level model
----------------

- Supervisor runs as a pod (typically a StatefulSet) deployed by your cluster install
  tooling.
- Home Assistant Core runs as a Kubernetes StatefulSet managed by Supervisor.
- Add-ons run as Kubernetes Deployments managed by Supervisor.
- Public exposure of the Home Assistant UI is handled by cluster GitOps (Gateway/HTTPRoute).
- LAN-only exposure of add-on TCP/UDP ports (MQTT, etc.) is handled by an internal
  LoadBalancer VIP managed by Supervisor.

Runtime selection
-----------------

Supervisor supports selecting the runtime backend via env:

- `SUPERVISOR_RUNTIME=docker` (default)
- `SUPERVISOR_RUNTIME=kubernetes`

When in Kubernetes mode, Docker-only components are disabled or treated as unsupported.
Many REST endpoints that are host/Docker specific return a consistent "not supported" API
error.

Storage
-------

The Kubernetes backend currently expects a shared RWX PVC that is mounted by Supervisor
and Home Assistant.

- Supervisor mounts the shared PVC at `/data`.
- Home Assistant mounts the shared PVC at `/config` with `subPath: homeassistant`.
- Add-ons mount the shared PVC:
  - `/data` with `subPath: addons/data/<addon_slug>`
  - `/homeassistant` with `subPath: homeassistant` (many add-ons expect HA config at this
    Docker-era path)

The Kubernetes backend ensures the shared PVC exists and matches expectations (RWX, storage
class, size). For MVP we support a single storage mode:

- `SUPERVISOR_K8S_STORAGE_MODE=shared_pvc`

Home Assistant workload (Kubernetes)
------------------------------------

Home Assistant Core is implemented as:

- StatefulSet `homeassistant` (replicas 0/1)
- Service `homeassistant` (ClusterIP, port 8123)
- Headless Service `homeassistant-headless` (for StatefulSet)

Supervisor injects the following integration-related env vars into the Home Assistant
container:

- `SUPERVISOR_TOKEN` and `HASSIO_TOKEN` (same token)
- `SUPERVISOR=supervisor` and `HASSIO=supervisor` (hostname only, no scheme)

Reverse proxy support (Gateway/Envoy)
-------------------------------------

When Home Assistant is behind a Gateway/Envoy dataplane, it will reject requests with
`X-Forwarded-For` unless configured with trusted proxies.

Supervisor (Kubernetes runtime) ensures Home Assistant has an `http:` section configured.
To avoid breaking YAML with custom tags (e.g. `!include`), Supervisor does not parse YAML.
Instead it appends a managed block if there is no existing top-level `http:` section.

Config knobs:

- `SUPERVISOR_K8S_HA_TRUSTED_PROXIES` (comma separated CIDRs)
  - default: `10.42.0.0/16`

Add-on workload (Kubernetes)
----------------------------

Each add-on is implemented as:

- Deployment `<sanitized-add-on-name>` (replicas 0/1)
- Service `<sanitized-add-on-name>` (ClusterIP)

Kubernetes names are sanitized to be DNS-safe (underscores become hyphens, lowercased).

Security constraints (MVP):

- No host networking
- No privileged containers
- No device passthrough

If an add-on requires unsupported features, Supervisor will refuse to run it in Kubernetes
runtime.

Add-on start/stop
-----------------

"Start" and "stop" scale the add-on Deployment.

Important detail:

- Supervisor generates the add-on token immediately before starting.
- In Kubernetes, scaling does not update the pod template, so the Kubernetes add-on backend
  ensures the Deployment template is patched with the latest token before scaling to 1.

Networking: public HA vs internal add-on ports
----------------------------------------------

This Kubernetes backend supports a two-VIP model:

1) Public HA web VIP (GitOps owned)

- A cluster-managed Gateway + HTTPRoute publishes the Home Assistant web UI (and the
  Supervisor ingress prefix `/api/hassio_ingress`).
- Supervisor can optionally manage this, but recommended ownership is GitOps.

2) Internal L4 VIP for add-on TCP/UDP ports (Supervisor owned)

- Supervisor manages a dedicated `Service type=LoadBalancer` bound to an explicitly
  configured address (VIP).
- Supervisor runs an in-cluster L4 proxy (TCP/UDP) behind that LoadBalancer.
- The proxy forwards traffic to the add-on's ClusterIP Service.
- This VIP is intended to be reachable only from LAN VLANs (IoT) via firewalling and
  routing. It is never WAN port-forwarded.

Supervisor only programs internal L4 exposure when an add-on explicitly exposes ports
(`ports` mapping with non-null external ports). Ingress-only add-ons do not require L4
exposure.

LoadBalancer provider notes
---------------------------

The internal VIP is requested via `spec.loadBalancerIP`, but many environments require
provider-specific annotations to ensure a deterministic VIP is allocated.

- Cilium LB IPAM: `io.cilium/lb-ipam-ips: <vip>`
- Configure via `SUPERVISOR_K8S_INTERNAL_L4_SERVICE_ANNOTATIONS` (JSON object), for example:

  `{ "io.cilium/lb-ipam-ips": "192.168.100.130" }`

Gateway API behavior
--------------------

Public gateway management (optional):

- `SUPERVISOR_K8S_MANAGE_PUBLIC_GATEWAY` (default false)
  - If true, Supervisor creates/patches a Gateway + HTTPRoute for HA + Supervisor ingress.
  - If false, Supervisor assumes GitOps already provides them.

Internal VIP for add-on ports (required for L4 exposure):

- `SUPERVISOR_K8S_INTERNAL_GATEWAY_ADDRESS` (example: `192.168.100.130`)
- `SUPERVISOR_K8S_INTERNAL_GATEWAY_CLASS` (optional; default: `cilium`)
- `SUPERVISOR_K8S_INTERNAL_GATEWAY_NAME` (default: `ha-internal`)
- `SUPERVISOR_K8S_INTERNAL_L4_IMAGE` (optional; default is `nginx:1.25-alpine`)

CRD requirements:

- HTTPRoute requires Gateway API HTTPRoute CRDs.
- TCP/UDP add-on exposure does not require Gateway API L4 CRDs.

RBAC expectations
-----------------

The Supervisor ServiceAccount must be able to manage the resources it creates.

Typical requirements in the `home-assistant` namespace:

- apps: Deployments (+ `deployments/scale`), StatefulSets (if Supervisor manages HA)
- core: Pods, Pods/log, Services, Endpoints, ConfigMaps, Secrets, Events, PVCs
- discovery.k8s.io: EndpointSlices (list/watch)
- gateway.networking.k8s.io:
  - Gateways
  - HTTPRoutes (only if `SUPERVISOR_K8S_MANAGE_PUBLIC_GATEWAY=true`)
  - (No L4 Gateway API resources are required for add-on port exposure)

Limitations
-----------

- Host integrations (DBus/OS/NetworkManager) are not supported.
- Docker plugins (DNS/Audio/Observer/etc.) are not supported.
- Some Supervisor API endpoints return "not supported" in Kubernetes runtime.

Debugging
---------

Useful checks:

- From inside the HA pod:
  - `curl -H "Authorization: Bearer $SUPERVISOR_TOKEN" http://supervisor/supervisor/info`
  - `curl -H "Authorization: Bearer $SUPERVISOR_TOKEN" http://supervisor/core/info`

- DNS/VIP correctness:
  - ensure `ha.example.com` resolves to the public Gateway VIP
  - ensure the internal add-on VIP is not reachable from WAN
