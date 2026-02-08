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
