# Media Architecture & Data Flow (Authoritative)

## Purpose

This document defines where media lives, how it is accessed,
and how compute services interact with stored data.

These decisions are intentional and form part of the homelab’s
zero-trust design.

---

## System Roles

### Atlas (NAS — SERVERS VLAN)

Role:
System of record for all persistent media and user data.

Responsibilities:
- Store all media and user data
- Serve data to clients and services
- Maintain parity and integrity

Data stored on Atlas:
- Movies
- TV Shows
- Music
- Photos
- Family documents
- Backups
- Application metadata (where appropriate)

Atlas is stateful and data-critical.

---

### Prometheus (Compute — SERVERS VLAN)

Role:
Compute and service host only.

Responsibilities:
- Run containers and services
- Consume media from Atlas
- Perform transcoding, indexing, AI tasks

Prometheus does NOT:
- Permanently store media
- Act as a backup target
- Provide file storage to users

Prometheus is stateless and rebuildable.

---

## Media Flow Model

[ Atlas (Storage) ]
        │
        │  NFS (preferred) / SMB
        │
[ Prometheus (Services) ]
        │
        │  HTTPS / Streaming
        │
[ USER Devices ]

## Media Automation Pipeline

Validated current-state media automation runs on [[systems/prometheus]]:

```text
Prowlarr
  -> Radarr / Sonarr
  -> qBittorrent
  -> Prometheus local staging
  -> Atlas managed media libraries
```

Prometheus local staging:

- Host path: `/opt/torrents/downloads`
- Container path: `/downloads`
- Classification: temporary local staging

Atlas final libraries:

- Movies: `/mnt/user/managed-media/movies`
- TV: `/mnt/user/managed-media/tv`

`/mnt/atlas/downloads` is not an active Atlas export.

---

## Key Rules

- USER devices access media only via Atlas SMB
- Services access media only via Prometheus
- USER devices never access Prometheus directly
- Prometheus never becomes the sole holder of data

---

## Security Implications

- Atlas is protected behind SERVERS VLAN firewall rules
- Prometheus can be rebuilt without data loss
- A compromised service does not compromise storage
- Zero-trust boundaries are preserved

---

🔒 Decision (Locked)

All media lives on Atlas.
Prometheus consumes media but never owns it.

---

🛑 Stopping Point

Media architecture is finalized.
Service deployment may proceed.
