# Home Assistant Supervisor on Kubernetes (Manifest Setup)

This repository is a fork of the upstream Home Assistant Supervisor.
It contains an experimental Kubernetes runtime backend that can manage add-ons on Kubernetes.

This document describes how to deploy Supervisor using the provided manifest
`ha-k8s-supervised.yaml`.

## What This Deploys

`ha-k8s-supervised.yaml` deploys **Supervisor only**:

- `persistentvolumeclaim/ha-shared-rwx` (shared RWX storage)
- `service/supervisor` (ClusterIP, port 80)
- `statefulset/supervisor` (Supervisor pod, Kubernetes runtime mode)

Supervisor then manages:

- Add-ons (as Deployments)
- Internal L4 port exposure for add-ons via:
  - `service/ha-internal` (type LoadBalancer, internal VIP)
  - `deployment/ha-internal` (NGINX stream proxy)
  - `configmap/ha-internal-config`

This manifest does **not** deploy:

- Home Assistant Core (that is expected to be deployed separately)
- Public ingress (Gateway/Ingress/HTTPRoute)

## Prerequisites

Because `ha-k8s-supervised.yaml` is designed to be applied with a **namespace-scoped
ServiceAccount kubeconfig**, it assumes these exist already (usually created by cluster
admin / GitOps):

- Namespace: `home-assistant`
- ServiceAccount: `home-assistant/supervisor`
- RBAC for that ServiceAccount granting permission to manage the namespaced resources
  Supervisor needs:
  - `apps`: deployments, deployments/scale, statefulsets, statefulsets/scale
  - core: services, configmaps, secrets, pods, pods/log, persistentvolumeclaims
  - optional: `gateway.networking.k8s.io` resources if you want Supervisor to clean up
    legacy Gateway API L4 objects

Cluster capabilities:

- A RWX-capable storage class (example: `cephfs`)
- Cilium LB IPAM (or another LoadBalancer provider)

## Configure The Manifest

Open `ha-k8s-supervised.yaml` and adjust:

- `storageClassName` and `SUPERVISOR_K8S_SHARED_PVC_STORAGE_CLASS`
- `storage` and `SUPERVISOR_K8S_SHARED_PVC_SIZE`
- `SUPERVISOR_K8S_INTERNAL_GATEWAY_ADDRESS` (internal VIP, e.g. `192.168.100.130`)

Image:

- Recommended: `image: shantur/homeassistant-kubernetes-supervisor:2026.01.2-1`
- Rolling: `image: shantur/homeassistant-kubernetes-supervisor:latest`

Home Assistant reverse proxy:

- If Supervisor is managing the Home Assistant Core workload on Kubernetes, it can
  configure `http.trusted_proxies` in `configuration.yaml`.
- Set `SUPERVISOR_K8S_HA_TRUSTED_PROXIES` (comma-separated CIDRs/IPs). Default k3s
  PodCIDR is typically `10.42.0.0/16`.

## Deploy

Apply the manifest:

```bash
kubectl --kubeconfig=cluster.kubeconfig -n home-assistant apply -f ha-k8s-supervised.yaml
```

Wait for Supervisor:

```bash
kubectl --kubeconfig=cluster.kubeconfig -n home-assistant rollout status statefulset/supervisor --timeout=10m
kubectl --kubeconfig=cluster.kubeconfig -n home-assistant get pods -l app=supervisor -o wide
kubectl --kubeconfig=cluster.kubeconfig -n home-assistant get svc supervisor -o wide
```

## Resources Created

After applying `ha-k8s-supervised.yaml`, you should have:

- `persistentvolumeclaim/ha-shared-rwx`
- `service/supervisor`
- `statefulset/supervisor`

Once Supervisor is running, it will create additional resources as you use it:

- Add-ons:
  - `deployment.apps/addon-<slug>`
  - `service/addon-<slug>`
- Internal add-on port exposure (only when an add-on exposes ports):
  - `service/ha-internal` (type LoadBalancer; internal VIP)
  - `deployment/ha-internal` (NGINX stream proxy)
  - `configmap/ha-internal-config`

Add-on logs:

- In Kubernetes runtime, add-on logs are served via the Kubernetes API (`pods/log`) instead
  of host journald.
- Live follow is supported using Kubernetes log streaming.

## Troubleshooting

- `Forbidden` errors applying the manifest:
  - Your kubeconfig likely lacks permissions to `get/create` the resources in the file.
  - This is expected if namespace/SA/RBAC are managed elsewhere.

- Supervisor starts but cannot manage Kubernetes resources:
  - Confirm in-cluster auth works (ServiceAccount token mounted automatically).
  - Check Supervisor logs for Kubernetes client errors.
  - Verify Role/RoleBinding for `home-assistant/supervisor` includes required verbs.

- Internal VIP not allocated:
  - Confirm your LoadBalancer implementation.
  - For Cilium LB IPAM, ensure the cluster is configured and that `service/ha-internal`
    has `io.cilium/lb-ipam-ips` annotation and `status.loadBalancer.ingress[].ip`.
