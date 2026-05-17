# Prometheus Media Stack Compose Scaffold

## Status

status: scaffold aligned to validated live media stack state

## Purpose

This folder contains a sanitized, Git-tracked Docker Compose scaffold for the Prometheus media stack.

The current live media stack is documented as deployed from:

```text
/opt/vpn/docker-compose.yml
```

This scaffold does not move or modify the live stack.

Validated live state for Milestone 9 records the media stack running on [[systems/prometheus]] from `/opt/vpn/docker-compose.yml`.

## Services

- Gluetun
- qBittorrent
- Prowlarr
- Radarr
- Sonarr

Jellyfin is not included yet because its live deployment details and storage paths still need validation.

## Secret Handling

- Do not commit the live `.env`.
- Do not commit VPN keys.
- Do not commit API keys.
- Do not commit passwords or tokens.
- Use `.env.example` as the placeholder reference only.

The repository ignores `.env` and `.env.*` while allowing `.env.example`.

## Network Model

qBittorrent uses:

```yaml
network_mode: service:gluetun
```

The qBittorrent WebUI is exposed through Gluetun only.

Validated live exposure:

| Service | Current bind | Classification |
|---|---|---|
| qBittorrent WebUI | `127.0.0.1:8080:8080` through Gluetun | Localhost-only |
| Prowlarr | `0.0.0.0:9696` | Temporary broad exposure |
| Radarr | `0.0.0.0:7878` | Temporary broad exposure |
| Sonarr | `0.0.0.0:8989` | Temporary broad exposure |

The broad Prowlarr/Radarr/Sonarr binds are documented as temporary current state. Do not expand exposure or add WAN/public access without a new approved architecture decision.

## Required Local File

Create this file locally on Prometheus:

```text
systems/prometheus/automation/docker/stacks/media/.env
```

Or render a deployment-local copy beside the live compose file at `/opt/vpn`.

Do not commit that file.

## Storage Paths

| Path Variable | Default Example | Classification | Notes |
|---|---|---|---|
| `GLUETUN_CONFIG_PATH` | `/opt/vpn/gluetun` | Persistent runtime / service config | VPN runtime config. Secrets must remain outside Git. |
| `QBITTORRENT_CONFIG_PATH` | `/opt/torrents/config` | Persistent runtime / service config | qBittorrent config state. |
| `PROWLARR_CONFIG_PATH` | `/opt/arr/prowlarr` | Persistent runtime / service config | Prowlarr config state. |
| `RADARR_CONFIG_PATH` | `/opt/arr/radarr` | Persistent runtime / service config | Radarr config state. |
| `SONARR_CONFIG_PATH` | `/opt/arr/sonarr` | Persistent runtime / service config | Sonarr config state. |
| `MEDIA_DOWNLOADS_PATH` | `/opt/torrents/downloads` | Prometheus-local staging / disposable | qBittorrent download staging. Not authoritative. |
| `ATLAS_MOVIES_PATH` | `/mnt/atlas/managed-media/movies` | Authoritative on Atlas | Radarr final library path mounted as `/movies`. |
| `ATLAS_TV_PATH` | `/mnt/atlas/managed-media/tv` | Authoritative on Atlas | Sonarr final library path mounted as `/tv`. |

The following Atlas NFS exports are validated as active:

- `192.168.60.102:/mnt/user/managed-media`
- `192.168.60.102:/mnt/user/shared-media`

The following Prometheus mounts are validated as active:

- `/mnt/atlas/managed-media`
- `/mnt/atlas/shared-media`

`/mnt/atlas/downloads` is not an active Atlas export. Downloads remain local on Prometheus at `/opt/torrents/downloads`.

Radarr and Sonarr require `SKIP_CHOWN=true` when writing to Atlas NFS-backed library mounts.

## Application Configuration Requirements

qBittorrent:

- Default save path: `/downloads`
- Category `radarr`: `/downloads/radarr`
- Category `sonarr`: `/downloads/sonarr`
- Category `mam`: `/downloads/mam`
- Category `manual`: `/downloads/manual`

Radarr:

- Root folder: `/movies`
- Download client: qBittorrent at `gluetun:8080`
- Download category: `radarr`

Sonarr:

- Root folder: `/tv`
- Download client: qBittorrent at `gluetun:8080`
- Download category: `sonarr`

Prowlarr:

- Radarr URL: `http://radarr:7878`
- Sonarr URL: `http://sonarr:8989`

These application settings were configured and validated through local APIs on 2026-05-16. Indexer definitions and end-to-end download/import behavior still need validation.

See [[architecture/storage-authority-map]] and [[architecture/container-lifecycle-policy]].

## Validation Commands

Run only when explicitly approved on Prometheus.

```bash
docker compose --env-file .env -f compose.yml config
docker compose --env-file .env -f compose.yml ps
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
curl -I http://127.0.0.1:${QBITTORRENT_WEBUI_PORT:-8080}
```

## Known Limitations

- Image tags are placeholders; live repositories were validated on 2026-05-16.
- Live `/opt/vpn/docker-compose.yml` may differ from this scaffold until reconciled by an approved live edit.
- Secrets model is not finalized.
- Jellyfin is intentionally excluded until documented in this milestone.
- This compose file is not proof that the services are deployed.
- Live SSH validation succeeded on 2026-05-16; use the validation procedure before changing live state.
- `/opt/vpn/.env` is permission-protected from the `alex` account in normal reads; do not loosen secret permissions without approval.
