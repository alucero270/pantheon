Below is a **completed, production-grade Atlas document** with all known gaps filled based on what we actually implemented.
This is written to be **copied directly into your repo** as a canonical system document.

I’ve kept decisions explicit, added missing sections, and avoided future-phase creep.

---

# Atlas — Unraid NAS (Authoritative Storage System)

## Role

Atlas is the **authoritative storage system** for the homelab.

It is **storage-first**, **headless**, and **compute-agnostic**.

### Responsibilities

* Persistent data storage
* Media libraries
* Backups
* Application data (Nextcloud, Jellyfin config, databases)
* 3D scan data (raw + processed)
* NFS exports for compute nodes

### Explicit Non-Responsibilities

* No routing or firewall duties
* No AI or GPU workloads
* No heavy compute workloads
* No VM hosting
* No dependency for Prometheus bootstrapping

Atlas prioritizes **data integrity and availability over performance**.

---

## Design Constraints (Locked)

* Atlas must never be required for routing or firewalling
* Atlas must never be the only admin path to infrastructure
* Atlas must not host heavy compute workloads
* Atlas must not host AI workloads
* Atlas must not be a dependency for Prometheus bootstrapping

🔒 **Decision (Locked)**
Atlas is a storage authority only. Any deviation requires an ADR.

---

## Platform

* **Hardware:** Dell PowerEdge R530
* **RAID Controller:** Dell PERC H730 (HBA / pass-through mode)
* **OS:** Unraid
* **Management model:** Web UI only (headless)
* **Primary VLAN (final):** SERVERS (VLAN 60)
* **Temporary VLAN (historical):** USER (documented exception during recovery)

---

## Hardware Configuration

### Disk Inventory

| Count | Size   | Type | Role                      |
| ----- | ------ | ---- | ------------------------- |
| 7     | 4 TB   | HDD  | Data disks                |
| 1     | 4 TB   | HDD  | Parity                    |
| 1     | 250 GB | NVMe | Cache (appdata, metadata) |

> All disks are presented individually to Unraid.
> RAID functionality on the H730 is **disabled**.

---

### Parity Strategy

* **Current parity:** 1× parity disk
* **Second parity:** Deferred

**Rationale**

* Array size is still moderate
* Capacity growth prioritized during early phase
* Second parity will be added once array exceeds growth threshold or risk profile changes

Parity changes require downtime and must be planned.

---

## Network Configuration

### VLAN Placement (Final)

| Interface | VLAN         | Purpose                    |
| --------- | ------------ | -------------------------- |
| NIC 1     | SERVERS (60) | SMB, NFS, services         |
| NIC 2     | MGMT (99)    | Administrative access only |

### Access Model

| Source           | Access     |
| ---------------- | ---------- |
| USER → Atlas     | SMB only   |
| USER → Nextcloud | HTTP/HTTPS |
| SERVERS → Atlas  | NFS / SMB  |
| MGMT → Atlas     | Unraid UI  |
| WAN → Atlas      | ❌ None     |

No direct WAN exposure is permitted.

---

## Storage & Filesystem

### Filesystems

* **Array disks:** XFS
* **Cache pool:** Btrfs (single-device)

### Cache Usage Policy

| Share          | Storage    |
| -------------- | ---------- |
| appdata        | Cache-only |
| system         | Cache-only |
| nextcloud-data | Array      |
| media          | Array      |
| backups        | Array      |

Cache exists to protect metadata and improve responsiveness — not as primary storage.

---

## Shares (Authoritative)

### Core Shares

| Share          | Purpose              |
| -------------- | -------------------- |
| appdata        | Container configs    |
| system         | Docker / system data |
| media          | Movies, TV, Music    |
| documents      | Family files         |
| backups        | Device backups       |
| nextcloud-data | Nextcloud user data  |
| scans          | 3D scan data         |

### Share Policy

* Allocation: High-water
* Split level: Automatic unless explicitly required
* Disk shares: Disabled
* User shares: Enabled

---

## Docker Usage (Restricted)

Docker is enabled on Atlas with **strict scope control**.

### Allowed Containers

* Nextcloud
* MariaDB (Nextcloud only)
* Redis (Nextcloud locking/cache)
* Jellyfin (storage-adjacent, low compute)

### Disallowed Containers

* Torrents
* AI workloads
* Transcoding workloads
* VM-like services
* Compute-heavy stacks

🔒 **Decision (Locked)**
Atlas runs **data-adjacent services only**.

---

## Nextcloud Integration

### Container

* Image: `linuxserver/nextcloud`
* Network: Custom bridge (`nextcloud_net`)
* Config path: `/mnt/user/appdata/nextcloud`
* Data path: `/mnt/user/nextcloud-data` → `/data`

### Data Strategy

* Data directory is defined **at install time**
* Data directory must never be repointed post-install
* Other Atlas shares are mounted via **External Storage** in Nextcloud

### Database

* MariaDB container dedicated to Nextcloud
* Database: `nextcloud`
* User: `nextcloud`
* Root access retained for recovery only

---

## Redis & Memory Caching

Redis is mandatory for stability.

### Redis Usage

* Transactional file locking
* Performance improvement
* Prevents database lock contention

### `config.php` (Required)

```php
'memcache.local' => '\OC\Memcache\APCu',
'memcache.locking' => '\OC\Memcache\Redis',
'redis' => [
  'host' => 'redis',
  'port' => 6379,
],
```

⚠️ Syntax errors (missing commas) will cause **internal server errors**.

---

## Administration & Recovery

### Unraid

* Web UI accessible only from MGMT VLAN
* No SSH required for normal operation

### Nextcloud Password Recovery

Passwords are recoverable without reinstall:

```bash
php /app/www/public/occ user:resetpassword <username>
```

Reinstallation is **never** the correct recovery path.

---

## Security Posture

### Current State

* No WAN exposure
* VLAN isolation enforced
* HTTPS pending (VPN / reverse proxy phase)

### Deferred Hardening

* HTTPS + HSTS
* Reverse proxy
* Email notifications
* AppAPI daemon

Deferred items are documented but not blockers.

---

## Backup Strategy

* Primary data resides on Atlas
* Backups target Atlas shares
* Compute nodes treat Atlas as source of truth
* Offsite strategy deferred to later phase

---

## Known Limitations

* No GPU acceleration
* Limited RAM (16 GB)
* Not suitable for real-time transcoding
* No high-IOPS workloads

These are **intentional constraints**.

---

## Validation Checklist

* [x] Disks visible individually
* [x] Array started and parity valid
* [x] Cache operational
* [x] SMB accessible from USER VLAN
* [x] NFS available for SERVERS VLAN
* [x] Docker running (restricted)
* [x] Nextcloud functional
* [x] Redis operational

---

## Documentation Stopping Point

Atlas is **functionally complete**.

Further changes must:

* Be documented
* Respect design constraints
* Include an ADR if they alter role or scope

