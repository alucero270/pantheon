# Prometheus AI Stack Bring‑Up (Authoritative Procedure)

> **Scope:** This procedure documents the complete, *validated* bring‑up of AI workloads on **Prometheus**, including all **non‑obvious constraints and troubleshooting outcomes** encountered during initial deployment.
>
> This document is intentionally comprehensive and serves as the **single source of truth** for rebuilding or auditing the AI stack on Prometheus.

---

## 1. Purpose & Design Context

This procedure exists to support the following architectural intent:

- Prometheus is **disposable compute** (no authoritative data)
- Atlas remains the **authoritative storage system**
- AI services must be:
  - GPU‑accelerated
  - Containerized
  - Secure by default (no unnecessary LAN exposure)

**Related documents:**
- [[systems/atlas/architecture/data-strategy]]
- [[systems/prometheus]]

---

## 2. System Prerequisites

### Hardware
- Host: **Prometheus**
- GPU: **NVIDIA RTX 4000 Ada Generation (~20 GB VRAM)**

### OS & Base Software
- Ubuntu Server (24.04)
- NVIDIA driver **590.x**
- Docker Engine (non‑snap)
- NVIDIA Container Toolkit

Validation:
```bash
nvidia-smi
```

Expected:
- GPU detected
- Driver loaded
- No errors

---

## 3. Storage Model (Critical)

AI workloads on Prometheus use **local storage only**. Nothing in this layout is authoritative.

### 3.1 NVMe (Fast / Read‑Heavy)
Mounted at `/mnt/local/nvme`

```
/mnt/local/nvme/ai/
├── cache/
├── models/                 # Shared AI models (read‑only to services)
├── services/
│   ├── comfy-mnt/          # REQUIRED single mount for ComfyUI (/comfy/mnt)
│   │   ├── ComfyUI/
│   │   ├── venv/
│   │   └── user/
│   └── ollama/             # Ollama runtime data (~/.ollama)
```

Ownership:
- `comfy-mnt` → **UID:GID 1024:1024** (mandatory, see §6)
- `models` → root/docker, mounted read‑only

### 3.2 SSD (Write‑Heavy)
Mounted at `/mnt/local/ssd`

```
/mnt/local/ssd/ai/
├── outputs/
│   └── comfy/              # Generated images / video
├── projects/
│   └── openwebui/          # OpenWebUI backend state
```

---

## 4. Services Installed

| Service     | Purpose | Notes |
|------------|--------|------|
| ComfyUI    | Image / media generation | GPU‑accelerated, strict UID rules |
| Ollama     | LLM runtime | Local models only |
| OpenWebUI  | LLM UI | Depends on Ollama |

See individual service docs under [[systems/prometheus/services/README|Prometheus Services]].

---

## 5. Docker Compose - Current Pattern

Last live validation: 2026-05-17

### Key Rules

- User-facing AI services use [[systems/prometheus/opt/stacks/ingress/traefik/traefik]] and the external `proxy` Docker network.
- OpenWebUI and ComfyUI do not publish host ports in live state.
- Ollama publishes `127.0.0.1:11434 -> 11434/tcp` for local API access.
- Ollama also has live Traefik labels for `ollama.home.arpa`; this conflicts with [[decisions/ADR-007-centralized-ingress-on-prometheus]] and needs a decision.
- No AI service should be exposed directly to the LAN through arbitrary host ports.

Historical localhost binding pattern:
```yaml
ports:
  - "127.0.0.1:8188:8188"
```

Current Traefik-label pattern is documented in [[systems/prometheus/opt/stacks/ingress/traefik/traefik]] and [[systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy-validation]].

---

## 6. ComfyUI Storage & UID Constraint (Non‑Obvious)

> ⚠️ **This section documents a critical constraint that caused multiple startup failures.**

### 6.1 Root Cause

The `mmartial/comfyui-nvidia-docker` image enforces **all** of the following at startup:

1. Container **must** run as UID/GID **1024:1024**
2. The path **`/comfy/mnt` itself** must be:
   - A **single bind mount**
   - Owned by **1024:1024** on the host

❌ Mounting only subdirectories (e.g. `/comfy/mnt/models`) **will fail**
❌ Docker `user:` overrides without matching ownership **will fail**

This behavior is enforced by the image’s init script and **cannot be bypassed**.

### 6.2 Required Solution

On the host:
```bash
sudo mkdir -p /mnt/local/nvme/ai/services/comfy-mnt
sudo chown -R 1024:1024 /mnt/local/nvme/ai/services/comfy-mnt
sudo chmod -R 775 /mnt/local/nvme/ai/services/comfy-mnt
```

In Docker Compose:
```yaml
volumes:
  - /mnt/local/nvme/ai/services/comfy-mnt:/comfy/mnt
```

Shared models are mounted **outside** `/comfy/mnt` and symlinked internally.

This decision is formalized in [[decisions/ADR-006-comfyui-storage-constraints]].

---

## 7. First‑Run Behavior (Expected)

On first startup, ComfyUI will:

- Clone the ComfyUI repository
- Create a Python virtual environment
- Download PyTorch + CUDA wheels (multi‑GB)

This can take **10–20 minutes**.

During this time:
- `curl` may fail
- Browser access will not work

This is normal.

---

## 8. Validation Checklist

### Containers
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Expected:
- `comfy` → Up
- `ollama` → Up
- `openwebui` → Up

### ComfyUI
```bash
curl -k --resolve comfy.home.arpa:443:127.0.0.1 https://comfy.home.arpa/
```

Expected:
- `200 OK`

### Logs
```bash
docker logs --tail=50 comfy
```

Expected:
- No UID/GID errors
- "Starting server"

---

## 9. Troubleshooting Appendix

### Issue: `wrong version number` (OpenSSL)
**Cause:** HTTPS used against HTTP‑only service

**Fix:**
```text
Use the documented Traefik URL for routed services, or use `http://127.0.0.1:<port>` only for services that intentionally publish localhost ports.
```

---

### Issue: `Directory /comfy/mnt owned by unexpected user/group`
**Cause:** Sub‑mounts used instead of a single `/comfy/mnt` bind mount

**Fix:**
- Mount `/comfy/mnt` as a single directory
- Ensure host ownership is 1024:1024

---

### Issue: Browser access fails but curl works
**Cause:** Access model mismatch, DNS issue, Traefik route issue, or a service that is intentionally bound to localhost only.

**Fix:**
- Confirm whether the service is supposed to be routed through Traefik or accessed through a local tunnel.
- Validate the relevant route with [[systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy-validation]].
- For Ollama, resolve the current `ollama.home.arpa` route drift before treating Traefik access as approved.

---

## 10. Status

- ✅ GPU validated
- ✅ AI services operational
- ✅ Storage model aligned with architecture
- ✅ Non‑obvious constraints documented

This document defines the **baseline** AI stack for Prometheus.
