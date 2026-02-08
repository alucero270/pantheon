<<<<<<< Updated upstream
---
type: system
hostname: prometheus
role: Disposable compute + GPU runtime
status: active
last_updated: 2026-01-23
---

# Prometheus

## Role in Pantheon

Prometheus is explicitly **not authoritative for data** and must be rebuildable without data loss.

See:
- [[architecture/prometheus]]
- [[decisions/ADR-003-disposable-compute-prometheus]]
- [[architecture/data-strategy]]

---

## Hardware
- Chassis: {{document if needed}}
- CPU: {{document if needed}}
- RAM: {{document if needed}}
- Storage:
  - OS Disk: SSD (boot + base system)
  - Local Scratch / NVMe: Disposable caches only
- NICs:
  - NIC 1: SERVERS VLAN (60) — service runtime
  - NIC 2: MGMT VLAN (99) — administrative access
- GPU:
  - Model: **NVIDIA RTX A4000 Ada**
  - Driver: NVIDIA proprietary driver (see [[procedures/prometheus-nvidia-runtime]])
  - Intended use:
    - AI / ML workloads
    - GPU-accelerated processing
    - Optional media transcoding (service-specific)

---

## Operating System
- OS: Ubuntu Server (LTS)
- Installation Type: Minimal (no desktop)
- Access: SSH only
- Package Management: APT (no snap-based Docker)

---

## Network
- VLANs:
  - **MGMT (99)** — administrative access only
  - **SERVERS (60)** — runtime/service traffic
- IP Assignment:
  - SERVERS VLAN: DHCP (current)
  - MGMT VLAN: Static or DHCP reservation recommended
- Firewall Zone:
  - Enforcement handled by Cerberus
  - No USER or GUEST VLAN access permitted

See:
- [[architecture/prometheus#Network containment]]
- [[notes/prometheus-ubuntu]]

---

## Storage Layout
Prometheus local storage is **not authoritative**. Durable and important data is hosted on Atlas and mounted via NFS.

| Mount | Purpose | Notes |
|------|--------|------|
| `/` | OS + base runtime | Rebuildable |
| `/var/lib/docker` | Container images/layers | Disposable |
| `/mnt/atlas` | Atlas NFS root | Required |
| `/mnt/atlas/appdata` | Container runtime state (RW) | Durable, stored on Atlas |
| `/mnt/atlas/datasets` | Compute datasets (RW as needed) | Promote outputs back to Atlas |
| `/mnt/atlas/managed-media` | Media libraries (RO) | Authoritative |
| `/mnt/atlas/shared-media` | Family media (RO) | Not service-owned |

Atlas shares follow the Array-only authoritative model.

See:
- [[architecture/data-strategy]]
- [[decisions/ADR-005-atlas-share-storage-model]]
- [[procedures/prometheus-nfs-mounts]]

---

## Services Hosted
- Docker Engine + Compose plugin (baseline runtime)
- NVIDIA driver + NVIDIA Container Toolkit
- (Optional) KVM/QEMU virtualization stack when required

> Individual application services must be documented under `services/` and reference this system plus the data strategy.

---

## Virtualization Stack (Optional)
- Hypervisor: KVM / QEMU
- Management: libvirt
- Policy:
  - CPU mode: host-passthrough
  - CPU overcommit: disabled
  - Memory overcommit: disabled
  - GPU passthrough: **not default** (container GPU runtime preferred)

---

## Backup & Recovery
- Backup Source:
  - Atlas (authoritative + runtime data)
- Backup Destination:
  - Defined by Atlas backup strategy
- Restore Posture:
  - Prometheus is rebuilt using documented procedures
  - No data restoration required on Prometheus itself

See:
- [[procedures/prometheus-docker-baseline]]
- [[procedures/prometheus-nvidia-runtime]]
- [[procedures/prometheus-nfs-mounts]]

---

## Monitoring
- Host Metrics:
  - CPU, memory, disk, network (when monitoring stack is enabled)
- GPU Metrics:
  - `nvidia-smi` baseline
  - Optional DCGM exporter
- Alerts (recommended):
  - GPU unavailable
  - NFS mounts unavailable
  - Disk pressure on local scratch

---

## Security Posture
- Admin Access:
  - SSH only
  - MGMT VLAN only
  - Key-based authentication preferred
  - Root login disabled
- Runtime Security:
  - No remote Docker API exposure
  - Services bind only to SERVERS VLAN IPs
  - Least-privilege mounts (RO/RW intent enforced via NFS)

See:
- [[architecture/prometheus]]
- [[architecture/data-strategy]]

---

## Known Limitations
- SERVERS VLAN currently uses DHCP; ensure stable addressing for service binds.
- GPU driver/kernel compatibility must be validated during upgrades.
- UID/GID consistency required between Prometheus and Atlas for NFS access.

---

## Related Docs
- Architecture:
  - [[architecture/prometheus]]
  - [[architecture/data-strategy]]
- ADRs:
  - [[decisions/ADR-003-disposable-compute-prometheus]]
  - [[decisions/ADR-005-atlas-share-storage-model]]
- Procedures:
  - [[procedures/prometheus-docker-baseline]]
  - [[procedures/prometheus-nvidia-runtime]]
  - [[procedures/prometheus-nfs-mounts]]
- Notes:
  - [[notes/prometheus-ubuntu]]
# Prometheus — Compute & Virtualization Node

## Role

Prometheus is the centralized **compute node** for the homelab.

It exists to run:
- Virtual machines
- Containers
- AI workloads
- 3D scan processing
- Media services
- Application services (Nextcloud runtime, Jellyfin, etc.)

Prometheus is **not** authoritative for data.
It is rebuildable at any time.

---

## Design Constraints (Locked)

- Prometheus must never be the sole holder of important data
- Prometheus must consume data from Atlas
- Prometheus may cache data, but caches are disposable
- Prometheus must not expose admin interfaces to USER or GUEST VLANs
- Prometheus must be manageable only from MGMT VLAN

🔒 **Decision (Locked)**  
Prometheus is disposable compute. Data persistence lives on Atlas.

---

## Platform

- OS: Ubuntu Server (LTS)
- Installation type: Minimal (no desktop)
- Access: SSH only
- Management VLAN: MGMT (admin access)
- Service VLAN: SERVERS (runtime traffic)

---

## Network Placement

### VLAN Assignment

| Interface | VLAN | Purpose |
|--------|------|--------|
| NIC 1 | SERVERS (60) | Service runtime |
| NIC 2 | MGMT (99) | Administrative access |

Rules:
- No USER or GUEST access permitted
- No Wi-Fi access
- Firewall enforcement handled by Cerberus

---

## Storage Model

### Persistent vs Disposable Storage

| Storage | Purpose | Backed Up |
|------|------|------|
| OS Disk (SSD) | `/` | Yes |
| VM / Docker Storage | Images & volumes | Yes |
| NVMe Scratch | AI models, caches | No |

Disposable storage may be wiped at any time.

---

### Authoritative Data Access

Prometheus consumes data from Atlas via:
- NFS (preferred)
- SMB (acceptable where required)

Prometheus must not:
- Store primary copies of media
- Store primary copies of documents
- Store primary copies of application data

---

## Access Model

### Administrative Access

- SSH access allowed **only from MGMT VLAN**
- Root login disabled
- Non-root admin user required
- SSH key authentication preferred

---

### Service Access

- Services bind only to SERVERS VLAN
- No services bind to USER-facing interfaces
- External exposure is forbidden until explicitly documented

---

## Virtualization Stack

### Hypervisor

- KVM / QEMU
- libvirt

### Baseline Packages

Installed packages include:
- qemu-kvm
- libvirt-daemon-system
- libvirt-clients
- bridge-utils
- virt-manager
- nfs-common
- cifs-utils
- htop
- tmux
- curl
- git

---

### Virtualization Policy

- CPU mode: host-passthrough
- CPU overcommit: disabled
- Memory overcommit: d
=======
---
type: system
hostname: prometheus
role: Disposable compute + GPU runtime
status: active
last_updated: 2026-01-23
---
# Prometheus

## Role in Pantheon
Prometheus is Pantheon’s centralized **disposable compute node**. It provides container and virtualization runtime, including GPU-accelerated workloads, while consuming durable and authoritative data from Atlas.

Prometheus is explicitly **not authoritative for data** and must be rebuildable without data loss.

See:
- [[architecture/prometheus]]
- [[decisions/ADR-003-disposable-compute-prometheus]]
- [[architecture/data-strategy]]

---

## Hardware
- Chassis: {{document if needed}}
- CPU: {{document if needed}}
- RAM: {{document if needed}}
- Storage:
  - OS Disk: SSD (boot + base system)
  - Local Scratch / NVMe: Disposable caches only
- NICs:
  - NIC 1: SERVERS VLAN (60) — service runtime
  - NIC 2: MGMT VLAN (99) — administrative access
- GPU:
  - Model: **NVIDIA RTX A4000 Ada**
  - Driver: NVIDIA proprietary driver (see [[procedures/prometheus-nvidia-runtime]])
  - Intended use:
    - AI / ML workloads
    - GPU-accelerated processing
    - Optional media transcoding (service-specific)

---

## Operating System
- OS: Ubuntu Server (LTS)
- Installation Type: Minimal (no desktop)
- Access: SSH only
- Package Management: APT (no snap-based Docker)

---

## Network
- VLANs:
  - **MGMT (99)** — administrative access only
  - **SERVERS (60)** — runtime/service traffic
- IP Assignment:
  - SERVERS VLAN: DHCP (current)
  - MGMT VLAN: Static or DHCP reservation recommended
- Firewall Zone:
  - Enforcement handled by Cerberus
  - No USER or GUEST VLAN access permitted

See:
- [[architecture/prometheus#Network containment]]
- [[notes/prometheus-ubuntu]]

---

## Storage Layout
Prometheus local storage is **not authoritative**. Durable and important data is hosted on Atlas and mounted via NFS.

| Mount | Purpose | Notes |
|------|--------|------|
| `/` | OS + base runtime | Rebuildable |
| `/var/lib/docker` | Container images/layers | Disposable |
| `/mnt/atlas` | Atlas NFS root | Required |
| `/mnt/atlas/appdata` | Container runtime state (RW) | Durable, stored on Atlas |
| `/mnt/atlas/datasets` | Compute datasets (RW as needed) | Promote outputs back to Atlas |
| `/mnt/atlas/managed-media` | Media libraries (RO) | Authoritative |
| `/mnt/atlas/shared-media` | Family media (RO) | Not service-owned |

Atlas shares follow the Array-only authoritative model.

See:
- [[architecture/data-strategy]]
- [[decisions/ADR-005-atlas-share-storage-model]]
- [[procedures/prometheus-nfs-mounts]]

---

## Services Hosted
- Docker Engine + Compose plugin (baseline runtime)
- NVIDIA driver + NVIDIA Container Toolkit
- (Optional) KVM/QEMU virtualization stack when required

> Individual application services must be documented under `services/` and reference this system plus the data strategy.

---

## Virtualization Stack (Optional)
- Hypervisor: KVM / QEMU
- Management: libvirt
- Policy:
  - CPU mode: host-passthrough
  - CPU overcommit: disabled
  - Memory overcommit: disabled
  - GPU passthrough: **not default** (container GPU runtime preferred)

---

## Backup & Recovery
- Backup Source:
  - Atlas (authoritative + runtime data)
- Backup Destination:
  - Defined by Atlas backup strategy
- Restore Posture:
  - Prometheus is rebuilt using documented procedures
  - No data restoration required on Prometheus itself

See:
- [[procedures/prometheus-docker-baseline]]
- [[procedures/prometheus-nvidia-runtime]]
- [[procedures/prometheus-nfs-mounts]]

---

## Monitoring
- Host Metrics:
  - CPU, memory, disk, network (when monitoring stack is enabled)
- GPU Metrics:
  - `nvidia-smi` baseline
  - Optional DCGM exporter
- Alerts (recommended):
  - GPU unavailable
  - NFS mounts unavailable
  - Disk pressure on local scratch

---

## Security Posture
- Admin Access:
  - SSH only
  - MGMT VLAN only
  - Key-based authentication preferred
  - Root login disabled
- Runtime Security:
  - No remote Docker API exposure
  - Services bind only to SERVERS VLAN IPs
  - Least-privilege mounts (RO/RW intent enforced via NFS)

See:
- [[architecture/prometheus]]
- [[architecture/data-strategy]]

---

## Known Limitations
- SERVERS VLAN currently uses DHCP; ensure stable addressing for service binds.
- GPU driver/kernel compatibility must be validated during upgrades.
- UID/GID consistency required between Prometheus and Atlas for NFS access.

---

## Related Docs
- Architecture:
  - [[architecture/prometheus]]
  - [[architecture/data-strategy]]
- ADRs:
  - [[decisions/ADR-003-disposable-compute-prometheus]]
  - [[decisions/ADR-005-atlas-share-storage-model]]
- Procedures:
  - [[procedures/prometheus-docker-baseline]]
  - [[procedures/prometheus-nvidia-runtime]]
  - [[procedures/prometheus-nfs-mounts]]
- Notes:
  - [[notes/prometheus-ubuntu]]
>>>>>>> Stashed changes
