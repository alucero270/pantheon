# /mnt/local/ssd/container-runtime

## Purpose

Container runtime storage on the local SSD.

## Current Live Paths

- `/mnt/local/ssd/container-runtime/containerd`
- `/var/lib/containerd` mounted from `/mnt/local/ssd/container-runtime/containerd`
- Docker data-root remains `/mnt/local/nvme/docker` as of 2026-05-21.

## Related Paths

- `/opt/containerd`
- `/mnt/local/nvme/docker`

## Status

Current live containerd runtime path. Any Docker consolidation from `/mnt/local/nvme/docker` to `/mnt/local/ssd/container-runtime/docker` requires a separate approved migration plan.
