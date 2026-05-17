# ComfyUI

Last validated: 2026-05-17

## Purpose
ComfyUI provides a node-based UI for **GPU-accelerated image and media generation** on [[systems/prometheus]].

This service is part of the Prometheus AI stack and is treated as **disposable compute** per [[systems/atlas/architecture/data-strategy]].

---

## Platform
- **Host:** [[systems/prometheus]]
- **Runtime:** Docker Engine + NVIDIA Container Toolkit
- **GPU:** NVIDIA RTX 4000 Ada Generation
- **Image:** `mmartial/comfyui-nvidia-docker:latest`
- **Compose path:** `/home/alex/stacks/ai/docker-compose.yml`

---

## Access

Live state exposes ComfyUI through [[systems/prometheus/services/traefik]].

- Host port: none published
- Container port: `8188/tcp`
- Traefik route: `https://comfy.home.arpa`
- Traefik service target: container port `8188`

Older docs described SSH-tunnel-only access. Current live state uses the Traefik Docker-provider pattern.

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

- [[decisions/ADR-006-comfyui-storage-constraints]]

---

## Deployment

ComfyUI is managed as part of the AI Docker Compose stack:

- Compose location: `~/stacks/ai/docker-compose.yml`
- Service name: `comfy`

Bring-up and troubleshooting are documented in:

- [[systems/prometheus/procedures/ai-stack-initialization]]

---

## Validation

### Service health
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "^comfy\b"
```

### HTTP reachability (on Prometheus)
```bash
curl -k --resolve comfy.home.arpa:443:127.0.0.1 https://comfy.home.arpa/
```

### GPU visible in container logs
```bash
docker logs --tail=50 comfy
```

---

## Notes

- First boot may take significant time due to PyTorch + CUDA wheel downloads.
- Keep the service bound to localhost unless explicitly designing a hardened LAN exposure model.


## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Prometheus |
| Host/system/device owner | Prometheus |
| Runtime type | GPU/Docker workload |
| Source of truth | [[decisions/ADR-006-comfyui-storage-constraints]] and [[systems/prometheus/procedures/ai-stack-initialization]] |
| Config path | `/home/alex/stacks/ai/docker-compose.yml` |
| Data path | `/mnt/local/nvme/ai/services/comfy-mnt`, `/mnt/local/nvme/ai/models`, `/mnt/local/ssd/ai/outputs/comfy` |
| Secret requirements | Do not commit secrets |
| Network ports | Container `8188/tcp`; Traefik route `comfy.home.arpa`; no host port |
| Dependencies | GPU runtime, Docker, local storage constraints |
| Backup requirement | No authoritative data; generated output handling needs validation before cleanup |
| Validation command | `curl -k --resolve comfy.home.arpa:443:127.0.0.1 https://comfy.home.arpa/` |
| Recovery procedure | [[systems/prometheus/procedures/ai-stack-initialization]] |
| Automation classification | Ansible candidate after GPU/runtime validation |
| Preferred automation tool | Ansible candidate after GPU/runtime validation |
