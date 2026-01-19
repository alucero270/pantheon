# Nextcloud — External Storage Architecture (Atlas)

## Purpose

This document defines the **authoritative external storage model** for Nextcloud running on **Atlas (Unraid)**.

The goal is to:
- Avoid vendor lock-in
- Preserve direct SMB/NFS access
- Ensure data survives container rebuilds
- Support future migration to Prometheus

Nextcloud **does not own primary data**.

---

## Design Principles (Locked)

- Nextcloud must never be the sole owner of files
- Data must remain usable outside Nextcloud
- Storage must survive container deletion
- Storage must survive application migration

🔒 **Decision (Locked)**  
Nextcloud uses *external storage mounts* exclusively for user content.

---

## Storage Authority

| System | Role |
|---|---|
| **Atlas** | Authoritative storage |
| **Nextcloud** | File access + sync layer |
| **Prometheus** | Future compute + proxy |
| **Clients** | SMB / WebDAV / App |

---

## Atlas Share Layout (Authoritative)

These shares already exist on Atlas:
```
/mnt/user/documents /mnt/user/media /mnt/user/photos /mnt/user/scans /mnt/user/backups /mnt/user/nextcloud-data
```

### Share Responsibilities

| Share | Purpose |
| :---: | :---: |
| documents | Personal files |
| media | Family media (non-Jellyfin-managed) |
| photos | Camera uploads |
| scans | 3D scan data |
| backups | Client backups |
| nextcloud-data | Nextcloud-native uploads only |

⚠️ Media consumed by Jellyfin **must remain outside Nextcloud control**.

---

## Container Mount Strategy

### Docker Volume Mappings

The Nextcloud container mounts Atlas shares as **read/write external paths**:

```text
/external/documents 
/external/media 
/external/photos /external/scans
```

#### Example Unraid mapping:

```text
/mnt/user/documents → /external/documents
/mnt/user/media     → /external/media
/mnt/user/photos    → /external/photos
/mnt/user/scans     → /external/scans
```

---

## Permissions (Required)
All external shares must be owned by the container user:

```bash
chown -R 99:100 /mnt/user/<share>
chmod -R 775 /mnt/user/<share>
```

Where:
UID 99 = nobody
GID 100 = users

---

## Nextcloud Configuration

### External Storage App

__App:__ External storage support
__Type:__ Local
__Authentication:__ None

### Path Mapping
| Display Name | Path |
| :----: | :----: |
|  Documents   | /external/documents |
|  Media | /external/media |
| Photos | /external/photos |
| Scans | /external/scans |

### Authentication Prompt

- Uses Nextcloud admin password
- ❌ Not Unraid root
- ❌ Not MariaDB credentials

### Data Directory (Clarification)

- Nextcloud’s internal data directory remains:
```bash
php occ config:system:get datadirectory
# /data
```

This directory is used only for:
- App uploads
- User caches
- Metadata

Primary files live on Atlas shares via external mounts.

---

## Why This Model Is Correct

__Advantages__
- Files accessible via SMB even if Nextcloud is down
- Safe with Redis file locking
- Easy migration to Prometheus
- Backup-friendly
- No data duplication
- Explicitly Not Supported
- Moving shares into /data
- Symlinks into /data
- Letting Nextcloud manage Jellyfin media
- Mounting /mnt/user wholesale

---

## Failure & Recovery Scenarios
| Scenario | Result |
| :----: | :----: |
| Nextcloud container deleted | Data intact |
| MariaDB reset | Data intact |
| Redis removed | Data intact |
| Atlas reboot | Data intact |
| Prometheus migration | Clean|