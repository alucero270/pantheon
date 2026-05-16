# Prometheus — Compute & Virtualization Node

## System Purpose

Prometheus provides rebuildable compute for Pantheon.

## Role

Ubuntu compute node for virtualization, containers, AI workloads, ingress, and service runtime.

## Responsibilities

- Run virtual machines and containers.
- Host AI workloads and local inference services.
- Host Prometheus-owned runtime services.
- Consume authoritative data from Atlas.
- Provide centralized ingress through Traefik where documented.

## Explicit Non-Responsibilities

- Do not act as authoritative storage.
- Do not hold the only copy of important data.
- Do not bypass Cerberus firewall policy.
- Do not expose admin interfaces to USER or GUEST VLANs.

## Network Placement

Prometheus is documented on the SERVERS VLAN for runtime traffic and the MGMT VLAN for administrative access.

## Data Ownership

Prometheus owns runtime and disposable compute state only. Authoritative data lives on [[systems/atlas]].

## Service Ownership

- [[systems/prometheus/inventory]]
- [[systems/prometheus/services/ai-runtime]]
- [[systems/prometheus/services/ollama]]
- [[systems/prometheus/services/openwebui]]
- [[systems/prometheus/services/comfyui]]
- [[systems/prometheus/services/traefik]]
- [[systems/prometheus/services/3d-scanning]]

## Procedure Index

- [[systems/prometheus/procedures/ai-stack-initialization]]
- [[systems/prometheus/procedures/ollama-model-management]]
- [[systems/prometheus/procedures/reverse-proxy]]
- [[systems/prometheus/procedures/reverse-proxy-validation]]

## Automation Classification

Automation ready / Ansible candidate

## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Prometheus |
| Host/system/device owner | Prometheus |
| Runtime type | Ubuntu compute, containers, AI workloads, ingress runtime |
| Source of truth | Documentation and Git-managed configuration; service-specific details need validation |
| Config path | Needs validation |
| Data path | Runtime/disposable local paths only; authoritative data lives on [[systems/atlas]] |
| Secret requirements | Do not commit secrets; final model is [[automation/policies/secrets-policy|Needs decision]] |
| Network ports | Needs validation from service docs |
| Dependencies | Atlas storage mounts where documented; Cerberus network policy; service-specific dependencies |
| Backup requirement | Rebuildable host; Git-backed configuration and service-specific recovery docs required |
| Validation command | Needs validation |
| Recovery procedure | [[systems/prometheus/procedures/README]] |
| Automation classification | Automation ready / Ansible candidate |
| Preferred automation tool | Ansible |

## Automation Index

- [[systems/prometheus/automation/README]]
- [[systems/prometheus/automation/ansible/README]]

## What Good Looks Like

Prometheus can be rebuilt from documentation without losing authoritative data, and every hosted service declares paths, ports, dependencies, validation, and recovery posture.

## What To Avoid

- Do not place authoritative data on Prometheus.
- Do not expose service ports directly unless documented and approved.
- Do not treat AI model caches or container state as authoritative.

## Existing System Notes

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
