# Atlas — Unraid NAS (Authoritative Storage System)

## Role

Atlas is the **authoritative storage system** for the homelab.

It is storage-first, headless, and compute-agnostic.

Responsibilities:
- Persistent data storage
- Media libraries
- Backups
- Application data (Nextcloud, Jellyfin config, databases)
- 3D scan data

Atlas is not a compute node and must remain stable above all else.

---

## Design Constraints (Locked)

- Atlas must never be required for routing or firewalling
- Atlas must never be the only admin path to infrastructure
- Atlas must not host heavy compute workloads
- Atlas must not host AI workloads
- Atlas must not be a dependency for Prometheus bootstrapping

🔒 **Decision (Locked)**  
Atlas is a storage authority only. Any deviation requires an ADR.

---

## Platform

- Hardware: Dell PowerEdge R530
- OS: Unraid
- Management model: Web UI only (headless)
- VLAN (final): SERVERS
- VLAN (temporary): USER (documented exception)

---

## Har
