---
type: architecture
status: draft
last_updated:
  "2026-01-23":
---
---
type: architecture
status: draft
last_updated:
  "2026-01-23":
---

# Prometheus — Disposable Compute & GPU Runtime Architecture

## Purpose
Prometheus exists to provide centralized, high-performance compute for Pantheon (containers, VMs, GPU workloads, batch processing) **without becoming a storage authority**. It is designed to be **rebuildable** and operationally replaceable, with durable data living on Atlas.

See:
- [[decisions/ADR-003-disposable-compute-prometheus]]
- [[architecture/data-strategy]]

## Scope
- In scope:
  - Container runtime platform (Docker Engine + Compose)
  - GPU acceleration for container workloads (NVIDIA driver + toolkit)
  - Virtualization / VM hosting (optional, when required by services)
  - Compute access to authoritative datasets via NFS mounts from Atlas
  - Local disposable scratch for performance-sensitive temporary artifacts
- Out of scope:
  - Being the authoritative home for any important dataset
  - Human-facing file sharing (SMB is for humans via Atlas)
  - Long-term persistence of appdata not anchored on Atlas
  - Direct internet exposure of admin interfaces (must be explicitly documented if ever allowed)

## Design Goals
- **Disposable compute:** Loss or rebuild of Prometheus must not imply loss of authoritative data.  
  See [[decisions/ADR-003-disposable-compute-prometheus]].
- **Separation of concerns:** Atlas is the single storage authority; Prometheus consumes data via NFS and produces outputs that are promoted back to Atlas.  
  See [[architecture/data-strategy#Authoritative vs Runtime vs Disposable]].
- **GPU-first runtime:** Enable repeatable GPU workloads in containers (AI inference, processing, transcoding when needed).
- **Network containment:** Administrative access only from MGMT; services bind only to SERVERS.  
  See [[notes/prometheus-ubuntu]].

## Non-Goals
- “Hyperconverged” storage + compute (explicitly rejected)
- Treating Prometheus as a backup target
- Treating Prometheus local disks as durable storage for important datasets
- Allowing USER/GUEST VLAN access to management planes or admin UIs

## System Overview
Prometheus is the Pantheon compute and virtualization node running Ubuntu Server. It hosts containerized and/or virtualized workloads and consumes authoritative and runtime data from Atlas, primarily via NFS.

Prometheus may maintain local caches and scratch space to improve performance, but those are explicitly **disposable** by design.  
See [[architecture/data-strategy]].

## Responsibilities
- Provide a stable and standardized container runtime for Pantheon workloads
- Provide GPU acceleration for container workloads
- Provide compute-side mounts to Atlas (NFS preferred) for:
  - Authoritative datasets (generally read-only)
  - Runtime/config state (read-write, but stored on Atlas)
- Ensure workload deployment is reproducible (procedures + validations)
- Ensure operational posture matches network access constraints (MGMT vs SERVERS)

## Dependencies
- Internal:
  - **Atlas** — authoritative storage and NFS exports  
    See [[architecture/atlas]] and [[decisions/ADR-005-atlas-share-storage-model]].
  - **Cerberus** — firewall and VLAN policy enforcement  
    See [[notes/prometheus-ubuntu]].
- External:
  - Ubuntu package repositories (OS updates)
  - Docker official repository (Docker Engine + Compose plugin)
  - NVIDIA repositories/tooling (container runtime integration)

## Constraints
- Hardware:
  - Must support GPU acceleration for target workloads
  - Local NVMe/scratch may exist but is not authoritative storage
- Network:
  - MGMT VLAN (99): administrative access only
  - SERVERS VLAN (60): service runtime traffic only
  - Must not expose admin interfaces to USER or GUEST VLANs
- Security:
  - SSH access allowed only from MGMT VLAN
  - No direct remote Docker API exposure
  - Least privilege for service containers; mount only required paths
- Budget:
  - Prioritize reproducibility and operational simplicity over complex, fragile optimizations

## Failure Modes
- What happens if this system is unavailable?
  - Compute workloads stop (containers/VMs unavailable)
  - Data remains safe and intact on Atlas
  - Services can be redeployed to a replacement compute node after baseline bring-up  
    See [[procedures/prometheus-docker-baseline]].
- Acceptable vs unacceptable failure:
  - Acceptable:
    - Loss of local scratch, caches, container images, transient processing outputs
    - Rebuild/reprovision of Prometheus
  - Unacceptable:
    - Prometheus being the only holder of any authoritative dataset
    - Uncontrolled write access from compute to authoritative Atlas shares

## Security Considerations
- Trust boundaries:
  - MGMT VLAN is a privileged administrative boundary
  - SERVERS VLAN is a runtime boundary; service traffic stays here
  - Atlas is authoritative; compute nodes are consumers
- AuthN/AuthZ expectations:
  - Admin access via SSH (key-based preferred); root login disabled
  - Container access controlled by network policy + least-privilege mounts
  - NFS permissions and mount options enforce RO/RW intent per dataset classification  
    See [[architecture/data-strategy#Authoritative vs Runtime vs Disposable]].

## Related Documents
- ADRs:
  - [[decisions/ADR-003-disposable-compute-prometheus]]
  - [[decisions/ADR-005-atlas-share-storage-model]]
- Procedures:
  - [[procedures/prometheus-docker-baseline]]
  - [[procedures/prometheus-nvidia-runtime]]
  - [[procedures/prometheus-nfs-mounts]]
- Architecture:
  - [[architecture/data-strategy]]
  - [[architecture/atlas]]
- Notes / System Context:
  - [[notes/prometheus-ubuntu]]
