# ADR: ComfyUI Storage & UID/GID Constraints

- **Status:** Accepted
- **Date:** 2026-01-25
- **Deciders:** Pantheon maintainers
- **Scope:** Prometheus (AI / GPU compute)

---

## Context

ComfyUI is deployed on **Prometheus** as part of the Pantheon AI stack. The chosen container image is `mmartial/comfyui-nvidia-docker`, selected for:

- Reliable NVIDIA GPU support
- CUDA / cuDNN compatibility
- Turnkey ComfyUI + Manager setup

During initial deployment, multiple startup failures revealed **non-obvious constraints** imposed by the image that directly affect storage layout, permissions, and Docker configuration.

These constraints are not generic Docker best practices and must be explicitly documented to ensure reproducibility.

Related documents:
- [[procedures/prometheus-ai-stack-bringup]]
- [[architecture/data-strategy]]
- [[systems/prometheus]]

---

## Decision

We will deploy ComfyUI on Prometheus with the following enforced constraints:

1. **Container UID/GID Enforcement**
   - ComfyUI containers must run as **UID 1024 / GID 1024**
   - Host directories used by ComfyUI must be owned by `1024:1024`

2. **Single Bind Mount Requirement**
   - The container path `/comfy/mnt` **must** be a single bind mount
   - Subdirectory-only mounts (e.g. `/comfy/mnt/models`) are not permitted

3. **Service-Owned State Directory**
   - A dedicated directory is used on the host:
     ```
     /mnt/local/nvme/ai/services/comfy-mnt
     ```
   - This directory is fully owned by UID/GID 1024

4. **Read-Only Shared Models**
   - Shared AI models are mounted **read-only** outside `/comfy/mnt`
   - Models are made visible to ComfyUI via symlink inside `/comfy/mnt`

5. **Disposable Compute Alignment**
   - All ComfyUI state is treated as disposable
   - No authoritative data is stored locally on Prometheus

---

## Rationale

### Why UID 1024 is enforced

The `mmartial/comfyui-nvidia-docker` image includes an init script that validates:

- Runtime UID/GID
- Ownership of `/comfy/mnt`

If these checks fail, the container exits immediately. This behavior cannot be overridden via Docker configuration.

### Why a single `/comfy/mnt` bind mount is required

Docker sub-mounts do **not** change ownership of the parent directory. As a result:

- `/comfy/mnt` remains owned by `root:root`
- The image’s startup validation fails

Mounting the entire directory ensures ownership is correctly perceived inside the container.

### Why models are read-only

- Prevents accidental modification or deletion
- Enables reuse across services
- Aligns with Pantheon’s data durability rules

---

## Consequences

### Positive

- Deterministic startup behavior
- Clear ownership boundaries
- GPU workloads are stable and reproducible
- Storage layout is explicit and auditable

### Negative

- Less flexibility in UID/GID mapping
- Storage layout is more rigid than typical Docker deployments
- Requires awareness when modifying mounts or paths

---

## Alternatives Considered

### Alternative 1: Different ComfyUI Image

Other images were considered but rejected due to:

- Weaker GPU support
- Lack of active maintenance
- Inconsistent CUDA compatibility

### Alternative 2: Running as Host UID

Rejected because the image explicitly enforces UID 1024 and exits otherwise.

---

## Outcome

This ADR formalizes the **non-negotiable constraints** required to run ComfyUI successfully on Prometheus and prevents future rework or accidental regressions.

All future ComfyUI deployments on Pantheon systems must conform to this decision.
