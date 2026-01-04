# Nextcloud — Authoritative Service Definition (Migration-Safe)

## Purpose

Nextcloud provides private cloud file storage, synchronization,
and collaboration services for the homelab.

This deployment is designed to:

- Keep **all data authoritative on Atlas**
- Allow **clean migration** to Prometheus later
- Avoid reinstall, reupload, or permission surgery
- Scale without architectural changes

This document defines the **service architecture and constraints**.  
Step-by-step rebuild procedures live in `procedures/`.

---

## Service Role

- User-facing application
- Stateful at the data layer
- Stateless at the compute layer
- Internal-only (no WAN exposure)

---

## Stack Decision (Locked)

| Component | Choice | Reason |
|---------|--------|--------|
| Nextcloud | LinuxServer.io container | Stable, well-documented |
| Database | MariaDB container | Required for scale & migration |
| Cache / Locking | Redis container | Transactional file locking |
| Web Server | Built into container | Simplicity |
| Reverse Proxy | Deferred | Will run on Prometheus later |
| Storage | Atlas bind-mounts | Authoritative data |

🚫 **Explicitly Disallowed**

- SQLite
- Snap-based Nextcloud
- Unraid plugin installs
- Data inside container layers

🔒 **Decision (Locked)**  
Nextcloud must be fully portable between compute nodes.

---

## Data & Directory Layout (Critical)

All Nextcloud state is stored **outside containers** on Atlas.

### Authoritative Paths (Atlas)

- `/mnt/user/appdata/nextcloud`
- `/mnt/user/appdata/mariadb-nextcloud`
- `/mnt/user/nextcloud-data`

### Container Mounts

| Container Path | Host Path |
|---------------|-----------|
| `/config` | `/mnt/user/appdata/nextcloud` |
| `/data` | `/mnt/user/nextcloud-data` |
| MariaDB data | `/mnt/user/appdata/mariadb-nextcloud` |

**Rules**

- `/data` **must never change**
- No data may live inside container layers
- Paths must remain identical after migration

---

## Initial Deployment State

- Containers currently run on **Atlas**
- Network mode: internal bridge
- Access: internal VLANs only
- Ports: temporary direct exposure (no proxy)

This state is intentional and temporary.

---

## Database Configuration (MariaDB)

### Database Model

- One dedicated database for Nextcloud
- One dedicated user
- Credentials used nowhere else

### Required Variables

- `MYSQL_ROOT_PASSWORD`
- `MYSQL_DATABASE=nextcloud`
- `MYSQL_USER=nextcloud`
- `MYSQL_PASSWORD=<strong password>`

Database data directory:

- `/mnt/user/appdata/mariadb-nextcloud`

---

## Redis Configuration (File Locking)

Redis is mandatory for stable operation.

### Purpose

- Transactional file locking
- Prevents sync corruption
- Improves performance under load

### Required `config.php` Entries

```php
'memcache.local' => '\OC\Memcache\APCu',
'memcache.locking' => '\OC\Memcache\Redis',
'redis' => [
  'host' => 'Redis-Nextcloud',
  'port' => 6379,
],
```
---
## Constraints
- Redis data is disposable
- Redis must never be exposed outside SERVERS VLAN
- Redis loss must not corrupt Nextcloud data

---

## Nextcloud Data Directory Validation
After installation, the following must exist under:
`
/mnt/user/nextcloud-data/
├── files/
├── uploads/
├── appdata_*
└── .ncdata
`

If data appears under:
`/mnt/user/appdata/nextcloud`

→ STOP — configuration is invalid

Permissions Model
`Container User
PUID: 99
PGID: 100`

Ownership Fix (If Required)
`
chown -R 99:100 /mnt/user/nextcloud-data
chown -R 99:100 /mnt/user/appdata/nextcloud`
Restart containers after correction.

Maintenance & Health Commands
Executed via occ inside the container:
`
php occ db:add-missing-indices
php occ maintenance:repair --include-expensive`
These resolve:
- Missing database indices
- Mimetype migration issues
- Performance warnings

---

## External Storage Integration
Nextcloud may mount additional Atlas shares using the
External Storage app.

Typical mounts:
- Documents
- Photos
- Media

These mounts:
- Reference Atlas storage
- Do not duplicate data
- Preserve backup coverage
 
 ---
 
## Migration Strategy (Authoritative)
This deployment supports lift-and-shift migration.

When Prometheus takes over:
1. Stop Nextcloud, MariaDB, Redis on Atlas
2. Mount the same directories via NFS:
   * /mnt/user/nextcloud-data
   * /mnt/user/appdata/nextcloud
3. Start identical containers on Prometheus

### Result
- Same users
- Same files
- Same configuration
- No data movement
### Explicit Non-Goals
- No WAN exposure yet
- No HTTPS yet
- No reverse proxy yet
- No cloud offloading yet
These are Phase 2 tasks.

---

## Known Issues & Lessons Learned
MGMT VLAN DNS
- Initial license activation failed due to blocked DNS
- Temporary USER VLAN placement resolved this
- This is documented and accepted

### Database Version Warning
- MariaDB 12.x exceeds Nextcloud’s official recommendations
- Currently stable
- No action required unless issues arise

---

## Validation Checklist
- Web UI accessible internally
- Data stored under /mnt/user/nextcloud-data
- Redis file locking enabled
- No admin warnings present
- Uploads and sync function correctly

---

🛑 Stopping Point

Nextcloud is operational, migration-safe,
and compliant with the homelab data strategy.
