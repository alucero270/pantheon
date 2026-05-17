# Media Architecture — Data Flow & Responsibility

This document defines how media data is stored, accessed,
and processed within the homelab.

It establishes authoritative ownership, access boundaries,
and service responsibilities.

This is an architectural document.

## Design Goals

- Centralize all media storage
- Prevent duplication of authoritative data
- Isolate compute workloads from storage responsibility
- Allow services to be rebuilt without data loss
- Preserve network segmentation and zero-trust boundaries

## System Roles

Media handling is split across two systems:

- Atlas — Authoritative storage
- Prometheus — Media compute and services

Each system has a strictly defined role.

## Atlas — Media Storage Authority

Atlas is the single source of truth for all media data.

Responsibilities include:

- Storing all media libraries
- Maintaining disk parity and integrity
- Providing data access to compute services
- Serving media to user devices via SMB

Examples of stored media:

- Movies
- TV shows
- Music
- Photos
- Home videos
- Archived recordings

Media data must never exist solely on compute systems.

## Prometheus — Media Compute

Prometheus is responsible for:

- Running media services
- Indexing media libraries
- Transcoding media streams
- Serving media over the network

Prometheus does not own media data.

If Prometheus is rebuilt or lost:
- Media data remains intact on Atlas
- Services can be redeployed without data migration

## Media Data Flow

Media data flows as follows:
1. Media is stored on Atlas
2. Prometheus mounts media directories from Atlas
3. Media services index and process data
4. User devices access media via services

Validated media automation flow:

```text
Prowlarr
  -> Radarr / Sonarr
  -> qBittorrent
  -> /opt/torrents/downloads on Prometheus
  -> /mnt/atlas/managed-media on Atlas
```

Downloads are Prometheus-local staging only. `/mnt/atlas/downloads` is not an active Atlas export.

Final managed media libraries live on Atlas:

- Movies: `/mnt/user/managed-media/movies`
- TV: `/mnt/user/managed-media/tv`

## Exposure Boundaries (Needs Validation)

The following exposure notes exist in repository documentation but are not yet validated against live service configuration:

- qBittorrent WebUI is intended to be localhost-only through Gluetun: `127.0.0.1:8080`.
- Prowlarr `0.0.0.0:9696`, Radarr `0.0.0.0:7878`, and Sonarr `0.0.0.0:8989` are documented as temporary broad binds.

Do not expose media admin services to WAN/public networks without an approved security/architecture decision.

## Jellyfin (Needs Validation)

Jellyfin is not documented as deployed on Prometheus by default. Treat Jellyfin-on-Prometheus as a migration candidate only.

Target media mount model before deployment:

```text
/mnt/atlas/managed-media:/media:ro
```

## Related Documents

- [[systems/atlas/architecture/media-data-flow]]
- [[systems/atlas/architecture/storage-authority-map]]
- [[systems/prometheus/architecture/storage-authority-map]]
- [[systems/prometheus/automation/docker/stacks/media/README]]
- [[systems/prometheus/inventory]]
- [[decisions/ADR-010-container-lifecycle-policy-prometheus]]

## Access Paths

### User Access

- Protocol: SMB
- Source: USER VLAN devices
- Target: Atlas
- Purpose: File management and manual access

### Service Access

- Protocol: NFS (preferred)
- Source: Prometheus
- Target: Atlas
- Purpose: Media indexing, streaming, transcoding

## Network Boundaries

- Atlas resides in the SERVERS VLAN
- Prometheus resides in the SERVERS VLAN
- User devices never directly access Prometheus services
- Firewall rules enforce strict access paths

## Security Implications

This architecture ensures:

- Compromise of a media service does not expose storage
- Compromise of a user device does not expose compute
- Media data remains protected by network segmentation
- No lateral movement between user devices and compute services

## Explicit Constraints

- Media data must not be duplicated across systems
- Media services must not write authoritative data
- Prometheus must not be treated as a storage system
- All persistent media data must reside on Atlas
- Radarr and Sonarr may write final managed media into Atlas-backed library paths, but Atlas remains the storage authority.
- qBittorrent downloads remain local on Prometheus until imported.

🛑 Stopping Point

This media architecture is authoritative.

All media services and procedures must conform
to this model unless the architecture is explicitly changed.
