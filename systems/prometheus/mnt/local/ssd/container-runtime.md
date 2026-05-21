# /mnt/local/ssd/container-runtime

## Purpose

Container runtime storage on the local SSD.

## Current Live Paths

- `/mnt/local/ssd/container-runtime/containerd`
- `/var/lib/containerd` mounted from `/mnt/local/ssd/container-runtime/containerd`

## Related Paths

- `/opt/containerd`
- `/mnt/local/nvme/docker`

## Status

Current live runtime path. Any consolidation with `/mnt/local/nvme/docker` requires a separate approved migration plan.
