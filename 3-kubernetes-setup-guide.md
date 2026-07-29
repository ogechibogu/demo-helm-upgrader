# Kubernetes Setup Guide

**Audience:** Ops engineers taking over platform management (GKE-based).
**Scope:** connecting `kubectl` to the GKE cluster, and day-to-day `kubectl` operations. Requires **1. Tool Installation Guide** and **2. gcloud Setup Guide** to be complete first.

---

## Prerequisites

- Tooling installed per **1. Tool Installation Guide**
- `gcloud` authenticated and configured per **2. gcloud Setup Guide**
- Cluster name and region/zone for the target environment (dev/qa/prod)

---

## Connecting to the GKE Cluster

### The standard command

```bash
gcloud container clusters get-credentials CLUSTER_NAME --region REGION --project PROJECT_ID
```
(use `--zone` instead of `--region` if the cluster is zonal)

This writes an entry into `~/.kube/config` and switches `kubectl`'s current context to it. The context name it generates is long and unwieldy:

```
gke_acme-prod-platform_us-central1_platform-prod-gke
```

If `kubectx` is used to switch clusters, that's what shows up in the list. To get a clean cluster-name-only context, rename it right after connecting:

```bash
kubectl config rename-context \
  gke_PROJECT_ID_REGION_CLUSTER_NAME \
  CLUSTER_NAME
```

### One-command version

Wrapping both steps into a single shell function so ops don't have to remember or hand-type the long context string:

**macOS/Linux — add to `~/.zshrc` or `~/.bashrc`:**
```bash
gke-connect() {
  local cluster=$1
  local location=$2   # region or zone
  local project=$3

  gcloud container clusters get-credentials "$cluster" \
    --region "$location" --project "$project" 2>/dev/null \
  || gcloud container clusters get-credentials "$cluster" \
    --zone "$location" --project "$project"

  kubectl config rename-context \
    "gke_${project}_${location}_${cluster}" "$cluster" 2>/dev/null

  kubectl config use-context "$cluster"
  echo "Connected. Current context: $(kubectl config current-context)"
}
```
Usage:
```bash
gke-connect platform-prod-gke us-central1 acme-prod-platform
```

**Windows PowerShell — add to `$PROFILE`:**
```powershell
function gke-connect {
    param(
        [Parameter(Mandatory)][string]$Cluster,
        [Parameter(Mandatory)][string]$Location,
        [Parameter(Mandatory)][string]$Project
    )

    gcloud container clusters get-credentials $Cluster --region $Location --project $Project 2>$null
    if ($LASTEXITCODE -ne 0) {
        gcloud container clusters get-credentials $Cluster --zone $Location --project $Project
    }

    kubectl config rename-context "gke_${Project}_${Location}_${Cluster}" $Cluster 2>$null
    kubectl config use-context $Cluster
    Write-Host "Connected. Current context: $(kubectl config current-context)"
}
```
Usage:
```powershell
gke-connect -Cluster platform-prod-gke -Location us-central1 -Project acme-prod-platform
```

### Verify the connection

```bash
kubectl config current-context     # should print just the cluster name
kubectl get nodes                  # confirms auth + network are working
kubectl cluster-info               # shows control plane / DNS endpoints
```

If `kubectl get nodes` fails with an auth-related error, check the `gke-gcloud-auth-plugin` setup from the Tool Installation Guide — that's the most common cause.

---

## What's Next

_(kubectl operations reference — get/describe/logs, troubleshooting CrashLoopBackOff, rollout status, namespace hunting, resource usage, etc. — to be added here.)_
