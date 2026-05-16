# Prometheus Media Stack Compose Scaffold

## Status

status: scaffold

## Purpose

This folder contains a sanitized, Git-tracked Docker Compose scaffold for the Prometheus media stack.

The current live media stack is documented as deployed from:

```text
/opt/vpn/docker-compose.yml
```

This scaffold does not move or modify the live stack.

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

All scaffolded web UIs bind to localhost until exposure is explicitly documented and validated.

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
| `MEDIA_CONFIG_ROOT` | `/opt/vpn/config` | Persistent runtime / Needs validation | Service config state |
| `MEDIA_DOWNLOADS_PATH` | `/opt/torrents` | Unknown / Needs validation | Determine whether contents are temporary downloads |
| `MEDIA_STAGING_PATH` | `/opt/media-staging` | Unknown / Needs validation | Staging must not become authoritative |
| `ATLAS_MEDIA_PATH` | `/mnt/atlas/media` | Authoritative on Atlas / Needs validation mount | Prometheus should consume read-only unless workflow is explicitly approved |

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

- Image tags are placeholders until the live stack is validated.
- Live `/opt/vpn/docker-compose.yml` may differ from this scaffold.
- Atlas media mount path needs validation.
- Secrets model is not finalized.
- Jellyfin is intentionally excluded until documented in this milestone.
- This compose file is not proof that the services are deployed.
