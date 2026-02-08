# ComfyUI

## Purpose
ComfyUI provides a node-based UI for **GPU-accelerated image and media generation** on [[systems/prometheus]].

This service is part of the Prometheus AI stack and is treated as **disposable compute** per [[architecture/data-strategy]].

---

## Platform
- **Host:** [[systems/prometheus]]
- **Runtime:** Docker Engine + NVIDIA Container Toolkit
- **GPU:** NVIDIA RTX 4000 Ada Generation

---

## Access

ComfyUI is bound to localhost on Prometheus.

- **HTTP:** `http://127.0.0.1:8188`

Remote access is performed via an SSH tunnel (see [[procedures/prometheus-ai-stack-bringup]]).

---

## Storage

### Data Classification
- **Disposable (runtime):** yes
- **Authoritative:** no

ComfyUI state and outputs are stored on Prometheus local disks and may be rebuilt at any time.

### Host Paths
- **ComfyUI runtime/state (NVMe):**
  - `/mnt/local/nvme/ai/services/comfy-mnt`  
  Mounted into container as `/comfy/mnt`.

- **Shared models (NVMe, read-only):**
  - `/mnt/local/nvme/ai/models`

- **Outputs (SSD):**
  - `/mnt/local/ssd/ai/outputs/comfy`

### Container Paths
- **Run root:** `/comfy/mnt`
- **Models:** `/comfy/mnt/models` (implemented via symlink to a read-only mount)
- **Outputs:** `/comfy/mnt/output`

---

## Critical Constraints

ComfyUI is deployed using the `mmartial/comfyui-nvidia-docker` image.

This image enforces strict startup validation:

- Container must run as **UID/GID 1024:1024**
- `/comfy/mnt` **must** be a single bind mount owned by 1024:1024

These constraints and the required storage layout are formalized in:

- [[ADR-006-comfyui-storage-constraints]]

---

## Deployment

ComfyUI is managed as part of the AI Docker Compose stack:

- Compose location: `~/stacks/ai/docker-compose.yml`
- Service name: `comfy`

Bring-up and troubleshooting are documented in:

- [[prometheus-ai-stack-initialization]]

---

## Validation

### Service health
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "^comfy\b"
```

### HTTP reachability (on Prometheus)
```bash
curl -I http://127.0.0.1:8188
```

### GPU visible in container logs
```bash
docker logs --tail=50 comfy
```

---

## Notes

- First boot may take significant time due to PyTorch + CUDA wheel downloads.
- Keep the service bound to localhost unless explicitly designing a hardened LAN exposure model.

