# /mnt/local/nvme/docker

## Purpose

Docker runtime artifacts and volumes observed on the NVMe mount.

## Status

Current live Docker data-root observed and validated on 2026-05-21 with `docker info`.

Normalize only after container runtime ownership, rollback, downtime tolerance, and migration are validated.

## Related Paths

- `/var/lib/containerd`
- `/var/lib/docker`
- `/mnt/local/ssd/container-runtime/containerd`
- `/opt/containerd`
- [[systems/prometheus/opt/containerd/README]]
- [[systems/prometheus/mnt/local/ssd/container-runtime]]
