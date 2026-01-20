# Nextcloud — External Storage Validation Checklist

## Purpose

This document defines a **repeatable validation procedure** to confirm
that Nextcloud external storage is configured correctly and safely.

This checklist must be run:
- After initial installation
- After container rebuilds
- After permission changes
- Before migrations to Prometheus

---

## Preconditions

- Atlas array is started
- Nextcloud container is running
- External storage support app is enabled
- Administrator access to Nextcloud UI and CLI

---

## 1. Container Mount Validation

### 1.1 Verify Docker Mounts

From Unraid UI or CLI, confirm the following mappings exist:

```text
/mnt/user/documents → /external/documents
/mnt/user/media     → /external/media
/mnt/user/photos    → /external/photos
/mnt/user/scans     → /external/scans
```

❌ /mnt/user must NOT be mounted wholesale
❌ /data must NOT contain authoritative files

---

## 2. Filesystem Permissions
### 2.1 Verify Ownership
Run on Atlas:

```bash
ls -ld /mnt/user/documents /mnt/user/media /mnt/user/photos /mnt/user/scans
```

Expected:
```bash
Owner: nobody

Group: users
```

### 2.2 Correct if Needed
```bash
Copy code
chown -R 99:100 /mnt/user/<share>
chmod -R 775 /mnt/user/<share>
```

---

## 3. Nextcloud Configuration Validation

### 3.1 External Storage Entries
In Nextcloud Admin UI → External Storage:
| Mount Name| Type| Path|
| :----: | :----: | :----: |
| Documents | Local | /external/documents |
| Media | Local | /external/media |
| Photos | Local | /external/photos |
| Scans | Local | /external/scans |

Authentication:
Type: None

Password prompt uses Nextcloud admin password

---

## 4. Data Directory Sanity Check

### 4.1 Confirm Internal Data Directory
```bash
Copy code
php /app/www/public/occ config:system:get datadirectory
```

Expected output:
```text
Copy code
/data
```

## 4.2 Verify No User Files Inside /data
```bash
Copy code
ls /data
```

Expected:
```
App folders
Cache directories
```
Metadata only

❌ No user document folders
❌ No media libraries

---

## 5. Functional Validation
### 5.1 Write Test (Nextcloud → Disk)
Upload a file via Nextcloud UI to an external mount

Confirm file appears in:

```bash
Copy code
/mnt/user/<share>
```

### 5.2 Write Test (Disk → Nextcloud)
Create a file via SMB in the share

Verify it appears in Nextcloud (after scan or refresh)

---

## 6. Failure Simulation (Optional but Recommended)

### 6.1 Container Restart
Stop Nextcloud container

Start container again

Verify:

- [] External mounts reconnect
- [] Files remain accessible

---

## 6.2 Database Restart
Restart MariaDB container

Verify no data loss

---

## 7. Compliance Check
All of the following must be true:
- [] External mounts present

- [] Permissions correct

- [] /data not authoritative

- [] SMB access works independently

- [] Nextcloud container can be deleted without data loss

If any check fails:

Stop further configuration

Correct before continuing

