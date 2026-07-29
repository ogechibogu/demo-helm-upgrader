# gcloud Setup Guide

**Audience:** Ops engineers taking over platform management (GKE-based).
**Scope:** authenticating and configuring `gcloud` on your machine. Requires tooling from **1. Tool Installation Guide** to already be installed. Connecting to the GKE cluster and all `kubectl` usage is covered in **3. Kubernetes Setup Guide**.

---

## Prerequisites

- Tooling installed per **1. Tool Installation Guide**
- A GCP identity (per the access matrix)
- Access already granted per the platform access matrix
- Target GCP Project ID(s) for dev/qa/prod

---

## Authentication

```bash
gcloud init
```

This opens a browser to authenticate (`gcloud auth login` under the hood) and lets you pick a default project interactively.

Headless/remote machine (no browser available):
```bash
gcloud auth login --no-launch-browser
```

Verify:
```bash
gcloud auth list     # your account should show, marked ACTIVE
```

---

## Setting the Active Project

```bash
gcloud config set project PROJECT_ID
```

Since you'll be working across dev/qa/prod projects, it's worth knowing you can switch anytime without re-running `init`:
```bash
gcloud config set project OTHER_PROJECT_ID
```

Optionally set a default region/zone so you don't have to pass `--region`/`--zone` on every future command:
```bash
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a
```

Verify:
```bash
gcloud config list     # shows active account, project, region, zone
```

---

## What's Next

At this point `gcloud` is installed, authenticated, and pointed at a project. Connecting `kubectl` to an actual GKE cluster (the `get-credentials` command, kubeconfig context renaming so `kubectx` shows clean cluster names, and all day-to-day `kubectl` operations) is covered in **3. Kubernetes Setup Guide**.

---

## Appendix: Testing This Guide on a Clean Machine

A fresh OS user account is enough — no gcloud config, no PATH entries, nothing left over from a real install:

- **macOS:** System Settings → Users & Groups → Add Account → new standard user → log in as them and run through the guide.
- **Windows:** Settings → Accounts → Family & other users → Add account → new local account → sign in and run through the guide.

If you need a genuinely separate OS install and can't download an ISO, browser/RDP cloud desktops sidestep the download restriction:
- **Windows:** Azure Virtual Desktop, Windows 365 Cloud PC, AWS WorkSpaces
- **macOS:** AWS EC2 Mac instances, MacStadium, MacinCloud

These are billed services — check with your team, and confirm whether device policy applies to them the same way it applies to ISOs.
