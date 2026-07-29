# Tool Installation Guide

**Audience:** Ops engineers taking over platform management (GKE-based).
**Scope:** installing all tooling needed before configuring `gcloud` or connecting to Kubernetes. Covered next in **2. gcloud Setup Guide** and **3. Kubernetes Setup Guide**.

**Prerequisite:** admin/install rights on your machine.

---

## macOS

### What gets installed

- **`gcloud`** — Google Cloud CLI, used to authenticate and manage GCP resources
- **`kubectl`** — talks to the Kubernetes API on the cluster
- **`gke-gcloud-auth-plugin`** — required by `kubectl` to authenticate against GKE; without it `kubectl` fails even if `gcloud` works fine
- **`kubectx` / `kubens`** — fast switching between cluster contexts and namespaces
- **`fzf`** — fuzzy finder, gives `kubectx`/`kubens` an interactive picker

### How to install

Using Homebrew (install from https://brew.sh first if not already present):

```bash
brew install --cask google-cloud-sdk
brew install kubectl
brew install kubectx
brew install fzf
```

If Homebrew isn't permitted by policy, install `gcloud` via the official installer instead:
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

Install the GKE auth plugin:
```bash
gcloud components install gke-gcloud-auth-plugin
```

Enable it — add to `~/.zshrc` or `~/.bashrc`:
```bash
export USE_GKE_GCLOUD_AUTH_PLUGIN=True
```

Verify:
```bash
gcloud --version
kubectl version --client
kubectx --help
```

---

## Windows

### What gets installed

- **`gcloud`** — Google Cloud CLI, used to authenticate and manage GCP resources
- **`kubectl`** — talks to the Kubernetes API on the cluster
- **`gke-gcloud-auth-plugin`** — required by `kubectl` to authenticate against GKE; without it `kubectl` fails even if `gcloud` works fine
- **`kubectl-ctx` / `kubectl-ns`** — the Windows-compatible equivalent of `kubectx`/`kubens` (the original is a bash script that doesn't run natively on Windows), installed as `kubectl` plugins via `krew`
- **`fzf`** — fuzzy finder; has native Windows support

### How to install

`gcloud`, via the official installer (GUI, user-level install — a signed Google installer, not a disk image, so it isn't subject to ISO download restrictions):

1. Download from https://cloud.google.com/sdk/docs/install and run `GoogleCloudSDKInstaller.exe`.
2. On the final screen, leave the `kubectl` component checked.

Alternative via **winget**:
```powershell
winget install --id Google.CloudSDK
```

Alternative via **Chocolatey**:
```powershell
choco install gcloudsdk -y
```

`fzf`:
```powershell
choco install fzf -y
# or
scoop install fzf
```

`kubectl-ctx` / `kubectl-ns` via `krew`:
```powershell
# 1. Install krew — see https://krew.sigs.k8s.io/docs/user-guide/setup/install/
# 2. Then install the plugins:
kubectl krew install ctx
kubectl krew install ns
```
Usage becomes `kubectl ctx` and `kubectl ns` instead of `kubectx`/`kubens`. If WSL2 is available, running the actual `kubectx`/`kubens` scripts inside WSL2 is an alternative that keeps the exact same command names.

Install the GKE auth plugin:
```powershell
gcloud components install gke-gcloud-auth-plugin
```

Enable it — add to `$PROFILE`:
```powershell
[Environment]::SetEnvironmentVariable("USE_GKE_GCLOUD_AUTH_PLUGIN", "True", "User")
```
Restart the terminal after setting this.

Verify:
```powershell
gcloud --version
kubectl version --client
kubectl ctx --help
```

---

## What's Next

With tooling installed, move to **2. gcloud Setup Guide** to authenticate and configure `gcloud` for your project(s).
