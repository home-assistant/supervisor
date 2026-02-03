# Home Assistant Supervisor on Kubernetes (Manifest Setup)

This repository contains an experimental Kubernetes runtime backend for Home Assistant
Supervisor.

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

- `image: shantur/homeassistant-kubernetes-supervisor:k8s-lb-fix3`

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

## Verify Supervisor API

With a namespace-scoped kubeconfig you may not have `pods/exec` or `port-forward`. The
recommended approach is a short-lived helper pod:

1) Mount the shared PVC at `/data`.
2) Read the Supervisor token from `/data/homeassistant.json`.
3) Call the Supervisor service (`http://supervisor`).

Example helper pod:

```bash
kubectl --kubeconfig=cluster.kubeconfig -n home-assistant apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: supervisor-api-smoke
spec:
  restartPolicy: Never
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: ha-shared-rwx
  containers:
    - name: runner
      image: python:3.13-alpine
      volumeMounts:
        - name: data
          mountPath: /data
      command: ["sh", "-lc"]
      args:
        - |
          set -e
          apk add --no-cache curl >/dev/null
          TOKEN="$(python3 -c 'import json; from pathlib import Path; obj=json.loads(Path("/data/homeassistant.json").read_text()); print(obj.get("access_token",""))')"
          curl -sS -H "Authorization: Bearer $TOKEN" http://supervisor/supervisor/info
EOF

kubectl --kubeconfig=cluster.kubeconfig -n home-assistant wait --for=jsonpath='{.status.phase}'=Succeeded pod/supervisor-api-smoke --timeout=120s
kubectl --kubeconfig=cluster.kubeconfig -n home-assistant logs supervisor-api-smoke
kubectl --kubeconfig=cluster.kubeconfig -n home-assistant delete pod supervisor-api-smoke --ignore-not-found
```

## Install + Start Mosquitto (MQTT)

Install and start using the same helper pod pattern (token + curl). Example API calls:

- Install:
  - `POST /addons/core_mosquitto/install`
- Start:
  - `POST /addons/core_mosquitto/start`
- Check status:
  - `GET /addons/core_mosquitto/info`

After it starts, Supervisor should create the internal VIP L4 stack.

## Verify Internal VIP (L4)

Check the internal LoadBalancer Service and proxy:

```bash
kubectl --kubeconfig=cluster.kubeconfig -n home-assistant get svc ha-internal -o wide
kubectl --kubeconfig=cluster.kubeconfig -n home-assistant get deploy ha-internal -o wide
kubectl --kubeconfig=cluster.kubeconfig -n home-assistant get cm ha-internal-config -o yaml
```

You should see:

- `service/ha-internal` is `type: LoadBalancer` with the configured VIP
- `deployment/ha-internal` is Ready
- `configmap/ha-internal-config` includes NGINX `stream {}` `listen` directives and
  `proxy_pass addon-core-mosquitto...:1883`

Connectivity test (from a short-lived pod):

```bash
kubectl --kubeconfig=cluster.kubeconfig -n home-assistant apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: l4-tcpcheck-1883
spec:
  restartPolicy: Never
  containers:
    - name: tcpcheck
      image: busybox:1.36
      command: ["sh", "-lc"]
      args:
        - |
          set -e
          nc -vz -w 3 192.168.100.130 1883
EOF

kubectl --kubeconfig=cluster.kubeconfig -n home-assistant wait --for=jsonpath='{.status.phase}'=Succeeded pod/l4-tcpcheck-1883 --timeout=120s
kubectl --kubeconfig=cluster.kubeconfig -n home-assistant logs l4-tcpcheck-1883
kubectl --kubeconfig=cluster.kubeconfig -n home-assistant delete pod l4-tcpcheck-1883 --ignore-not-found
```

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
