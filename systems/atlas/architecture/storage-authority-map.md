# Atlas Storage Authority Map

## Purpose

This map classifies important Atlas paths as authoritative, persistent runtime, disposable, or unknown.

Atlas is the authoritative storage system for Pantheon.

## Controlling Rules

- Atlas is authoritative storage: [[decisions/ADR-002-atlas-as-storage]]
- Atlas authoritative shares are array-only: [[decisions/ADR-005-atlas-share-storage-model]]
- Pantheon data strategy: [[systems/atlas/architecture/data-strategy]]

## Atlas Paths

| Path | Purpose | Used By | Authority Classification | Backup Requirement | Migration Notes |
|---|---|---|---|---|---|
| `/mnt/user/documents` | User documents external storage | Nextcloud external storage, SMB clients | Authoritative | Required | Array-only; do not move without backup/restore plan |
| `/mnt/user/media` | User media external storage | Nextcloud external storage, SMB clients | Authoritative | Required | Distinct from Jellyfin-managed media; validate before exposing to services |
| `/mnt/user/photos` | User photos external storage | Nextcloud external storage, SMB clients | Authoritative | Required | Array-only authoritative data |
| `/mnt/user/scans` | Scan data external storage | Nextcloud external storage, 3D scanning workflows | Authoritative | Required | Prometheus may process copies; final authoritative data belongs on Atlas |
| `/mnt/user/backups` | Client and system backups | Atlas backup workflows | Authoritative | Required | Must remain protected and recoverable |
| `/mnt/user/nextcloud-data` | Nextcloud data directory | [[systems/atlas/services/nextcloud]] | Authoritative | Required | Must not be replaced by container-layer storage |
| `/mnt/user/appdata/nextcloud` | Nextcloud application configuration/state | [[systems/atlas/services/nextcloud]] | Persistent runtime / Service-critical | Required for service recovery | Treat as recovery data, not disposable cache |
| `/mnt/user/appdata/mariadb-nextcloud` | MariaDB data for Nextcloud | [[systems/atlas/services/mariadb]] | Authoritative service data | Required | Database backup/restore must be validated before migration |
| `/mnt/user/appdata` | Atlas Docker application data parent | Atlas Docker services | Persistent runtime / Service-critical | Required per-service | Classify per-service; not all appdata has equal importance |
| `/mnt/user/shared-media` | Authoritative media share named in ADR-005 | Media workflows | Authoritative | Required | Array-only; cache usage prohibited |
| `/mnt/user/managed-media` | Authoritative media share named in ADR-005 | Managed media workflows | Authoritative | Required | Array-only; Prometheus may consume but not own |

## Atlas Cache / Prohibited Authority

| Path | Purpose | Used By | Authority Classification | Notes |
|---|---|---|---|---|
| `/mnt/cache/<authoritative-share>` | Cache residue check path | Atlas share audit | Not authoritative / Should be empty | ADR-005 prohibits authoritative data on cache for authoritative shares |

## Migration Rules

- Do not move authoritative Atlas paths without verified backup, restore, and rollback.
- Do not treat Docker/container-layer state as authoritative.
