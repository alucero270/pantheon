---
type: adr
adr_id: ADR-006
status: accepted
date: 2026-01-23
---

# ADR-006: Prometheus Container Runtime and NVIDIA GPU Enablement

## Context
Prometheus is designated as a **disposable compute node** within Pantheon. It must provide a reliable, reproducible container runtime with GPU acceleration while ensuring that no authoritative data is stored locally.

Several container runtime and GPU enablement options exist on Ubuntu Server, including snap-based Docker installs, rootless container runtimes, alternative runtimes (Podman), and multiple NVIDIA integration paths. Some of these options introduce operational complexity, incompatibility with GPU workloads, or conflict with the NFS-based storage model.

This decision establishes a **single, standardized bring-up path** for Prometheus that is compatible with:
- NVIDIA RTX A4000 Ada GPU workloads
- Docker-based services
- NFS-mounted authoritative data from Atlas
- Rebuildability and operational clarity

See:
- [[architecture/prometheus]]
- [[systems/prometheus]]
- [[decisions/ADR-003-disposable-compute-prometheus]]

---

## Decision
Prometheus SHALL use:

1. **Docker Engine installed from the official Docker APT repository**
   - Docker Compose via the official Compose plugin
   - Snap-based Docker installs are explicitly disallowed

2. **NVIDIA proprietary drivers installed via Ubuntu-supported packages**

3. **NVIDIA Container Toolkit** for GPU access inside Docker containers

4. **Rootful Docker with controlled user access**
   - Non-root users granted access via the `docker` group
   - Rootless Docker is not used on Prometheus

This configuration is the **only supported container + GPU runtime** for Prometheus.

---

## Rationale
This approach was chosen because it:

- Is the **industry-standard** deployment model for Docker on Ubuntu Server
- Is fully compatible with NVIDIA GPUs and the NVIDIA Container Toolkit
- Avoids known issues with:
  - Snap confinement
  - Rootless Docker + GPU support
  - Rootless Docker + NFS permissions
- Provides predictable behavior across rebuilds
- Aligns with Prometheus being disposable compute and Atlas being authoritative storage

The Docker + NVIDIA Container Toolkit combination is well-documented, actively maintained, and widely used in production GPU environments.

---

## Alternatives Considered

- **Snap-based Docker**
  - Rejected due to confinement issues, opaque updates, and incompatibility with low-level GPU and filesystem integrations.

- **Rootless Docker**
  - Rejected due to:
    - Incomplete or fragile NVIDIA GPU support
    - UID/GID complexity with NFS-mounted Atlas shares
    - Increased operational complexity for limited security gain in a controlled MGMT environment

- **Podman / Podman + NVIDIA**
  - Rejected to avoid introducing a second container ecosystem and tooling divergence without clear benefit for Pantheon.

- **GPU passthrough to VMs**
  - Rejected as the default approach in favor of container-native GPU workloads.
  - May be revisited for specialized workloads.

---

## Consequences

### Positive
- Clear, repeatable Prometheus bring-up process
- Reliable GPU access for container workloads
- Minimal friction with NFS-mounted Atlas storage
- Simplified documentation and support model

### Negative
- Docker group membership is effectively root-equivalent
- GPU workloads depend on kernel/driver compatibility
- Less isolation than a fully
