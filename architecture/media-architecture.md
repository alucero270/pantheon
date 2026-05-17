# Media Architecture

## Purpose

This document records the Pantheon-wide media pipeline and points to system-owned architecture documents.

## Scope

- In scope: Atlas media authority, Prometheus media runtime, media automation flow, storage boundaries
- Out of scope: WAN/public exposure, Jellyfin deployment, copyrighted download validation

## System Overview

Media authority and media runtime are split:

- [[systems/atlas]] is authoritative storage.
- [[systems/prometheus]] is disposable compute, ingress, media automation runtime, and temporary download staging.

## Current Media Pipeline

```text
Prowlarr
  -> Radarr / Sonarr
  -> qBittorrent
  -> /opt/torrents/downloads on Prometheus
  -> /mnt/atlas/managed-media on Atlas
```

## Storage Boundaries

| State | Location | Classification |
|---|---|---|
| qBittorrent downloads | `/opt/torrents/downloads` on Prometheus | Temporary local staging |
| Movie library | `/mnt/atlas/managed-media/movies` on Prometheus, backed by Atlas | Authoritative on Atlas |
| TV library | `/mnt/atlas/managed-media/tv` on Prometheus, backed by Atlas | Authoritative on Atlas |
| Shared media | `/mnt/atlas/shared-media` on Prometheus, backed by Atlas | Authoritative on Atlas |
| Downloads on Atlas | `/mnt/atlas/downloads` | Not active / not an export |

## Exposure Boundaries

- qBittorrent WebUI is localhost-only through Gluetun: `127.0.0.1:8080`.
- Prowlarr `0.0.0.0:9696`, Radarr `0.0.0.0:7878`, and Sonarr `0.0.0.0:8989` are temporary current-state broad binds.
- Do not expose media admin services to WAN/public networks without an approved architecture/security decision.

## Jellyfin

Jellyfin is not documented as deployed on Prometheus.

Target media mount before deployment:

```text
/mnt/atlas/managed-media:/media:ro
```

Status: Needs validation.

## Related Documents

- [[systems/atlas/architecture/media-architecture]]
- [[systems/atlas/architecture/media-data-flow]]
- [[systems/atlas/architecture/storage-authority-map]]
- [[systems/prometheus/architecture/storage-authority-map]]
- [[systems/prometheus/automation/docker/stacks/media/README]]
- [[systems/prometheus/inventory]]
- [[decisions/ADR-010-container-lifecycle-policy-prometheus]]
