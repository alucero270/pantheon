# Data Strategy — Authoritative Design

This document defines where data lives, what is backed up,
what is disposable, and how data moves between systems.

This is an authoritative declaration.

---

## Data Classification Model

### 1. Authoritative (Persistent) Data

Must survive any failure or rebuild.

Examples:
- Family documents
- Media libraries
- Photos
- Backups
- Application data (Nextcloud, Jellyfin config)
- Raw and processed 3D scans

Location:
➡ Atlas (NAS)

Protection:
- Parity
- Snapshots (future)
- Backup (future offsite)

---

### 2. Runtime / Config State

Important but rebuildable if backed up.

Examples:
- Container configurations
- Application databases
- Service metadata

Location:
- Stored on Atlas
- Mounted into containers or VMs running on Prometheus or Atlas

Rule:
No service may store its only copy of configuration on a compute node.

---

### 3. Disposable / Ephemeral Data

Safe to lose.

Examples:
- AI model caches
- Embeddings
- Transcoding buffers
- Scratch datasets
- VM temporary disks

Location:
- Local disks on Prometheus
- NVMe scratch storage

Rule:
Disposable data is never backed up.

---

## Storage Authority Declaration

### Atlas (Authoritative Storage)

Atlas is the single source of truth for all persistent data.

Atlas stores:
- Media
- Documents
- Backups
- Application data
- 3D scan data

Atlas does not store:
- VM OS disks
- AI model caches
- Compute scratch space

Atlas failures must never result in silent data loss.

---

### Prometheus (Compute)

Prometheus is a disposable compute node.

Prometheus may:
- Process data
- Cache data
- Generate outputs

Prometheus must never be the only location of important data.

---

## Protocol Strategy (Architectural)

### SMB — Human Access

Used by:
- Nomad
- Ares
- Family devices

Characteristics:
- User-based authentication
- Familiar UX
- Mapped drives

---

### NFS — Compute Access

Used by:
- Prometheus
- Linux VMs
- Containers

Characteristics:
- High throughput
- POSIX permissions
- Stable mounts

---

🛑 Stopping Point

Data authority and classification are finalized.
All systems and services must conform to this model.
