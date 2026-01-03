# Data Strategy (Authoritative)

## Data Classification

### Authoritative (Persistent)
- Media
- Documents
- Photos
- Backups
- Nextcloud data
- 3D scan data

Location: Atlas

### Runtime / Config
- Container configs
- Databases

Location: Atlas-mounted into compute

### Disposable
- AI models
- Transcode caches
- Scratch data

Location: Prometheus local storage

## Storage Authority

Atlas is the single source of truth.
Prometheus is disposable.
