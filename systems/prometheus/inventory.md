# Prometheus Service Inventory

## Purpose

This document maps Prometheus service and container inventory before cleanup, migration, or stack normalization.

No services are deleted, moved, stopped, or modified by this inventory.

## Evidence Boundary

Use repository evidence and explicitly provided validated live state only.

Rows marked `Needs validation` identify services, containers, paths, ports, or images requested for inventory but not proven by the current repository documentation or validated live-state evidence.

Direct SSH revalidation from this workstation succeeded on 2026-05-16. The media stack rows below are reconciled from live Prometheus evidence and the validated state supplied for Milestone 9.

## Related Docs

- [[systems/prometheus]]
- [[systems/prometheus/architecture/compose-registry]]
- [[architecture/storage-authority-map]]
- [[architecture/container-lifecycle-policy]]
- [[systems/prometheus/services/README]]
- [[systems/prometheus/procedures/ai-stack-initialization]]
- [[systems/prometheus/procedures/reverse-proxy]]
- [[systems/prometheus/procedures/reverse-proxy-validation]]
- [[automation/policies/automation-classification]]

## Current Path Drift

Prometheus documentation currently shows three deployment/data patterns:

| Path Pattern | Evidence | Current Meaning | Drift / Risk | Recommended Action |
|---|---|---|---|---|
| `/opt/traefik` | [[systems/prometheus/services/traefik]], [[systems/prometheus/procedures/reverse-proxy]] | Reverse proxy deployment and config root | Separate from `~/stacks` and `/mnt/local`; may be intentional for infra ingress | Keep until compose/config source of truth is validated |
| `/opt/vpn/docker-compose.yml` | Validated live state for Milestone 9, [[systems/prometheus/automation/docker/stacks/media/README]] | Live media stack compose file | Git scaffold may differ from live compose until approved reconciliation | Keep; reconcile through media scaffold and validation procedure |
| `~/stacks/ai/docker-compose.yml` | [[systems/prometheus/services/comfyui]] | AI Docker Compose stack location | Shell-home-relative path; owner and backup posture need validation | Normalize documentation after compose inventory |
| `/mnt/local/nvme/ai/...` | [[systems/prometheus/procedures/ai-stack-initialization]], [[systems/prometheus/services/ollama]], [[systems/prometheus/services/comfyui]] | Fast local runtime/model/service data | Disposable local data, but still operationally important | Keep as local runtime path; validate ownership and mount state |
| `/mnt/local/ssd/ai/...` | [[systems/prometheus/procedures/ai-stack-initialization]], [[systems/prometheus/services/openwebui]], [[systems/prometheus/services/comfyui]] | Write-heavy local project/output data | Disposable local data; output handling needs validation | Keep as local runtime/output path; validate backup expectation |

## Lifecycle Classifications

| Classification | Meaning |
|---|---|
| Active documented | Current repo documents the service as active or operational |
| Active needs validation | Requested inventory item, but repo lacks enough evidence to prove deployment details |
| Questionable / exited needs validation | Requested questionable or exited container; repo lacks live evidence |
| Disposable runtime | Data or state can be rebuilt and is not authoritative |
| Cleanup candidate | Do not remove yet; requires live validation and rollback plan |

## Active Documented Inventory

| Service / Stack | Container Name | Image | Compose Path | Host Data Paths | Container Paths | Ports / Exposure | Lifecycle Classification | Recommended Action |
|---|---|---|---|---|---|---|---|---|
| AI stack | `comfy`, `ollama`, `openwebui` | Mixed; see service rows | `~/stacks/ai/docker-compose.yml` for ComfyUI; full stack compose path needs validation | `/mnt/local/nvme/ai/`, `/mnt/local/ssd/ai/` | See service rows | Localhost-only pattern documented | Active documented / Needs validation | Validate compose file contents before cleanup or automation |
| ComfyUI | `comfy` | `mmartial/comfyui-nvidia-docker` | `~/stacks/ai/docker-compose.yml` | `/mnt/local/nvme/ai/services/comfy-mnt`, `/mnt/local/nvme/ai/models`, `/mnt/local/ssd/ai/outputs/comfy` | `/comfy/mnt`, `/comfy/mnt/models`, `/comfy/mnt/output` | `127.0.0.1:8188`; SSH tunnel for remote access | Active documented / Disposable runtime | Keep; validate GPU/runtime and UID/GID ownership before automation |
| Ollama | `ollama` | Needs validation | AI stack compose path needs validation | `/mnt/local/nvme/ai/services/ollama` | `/root/.ollama` | `127.0.0.1:11434 -> 11434/tcp` | Active documented / Disposable runtime | Keep; validate image tag, compose path, and model cache policy |
| OpenWebUI | `openwebui` | Needs validation | AI stack compose path needs validation | `/mnt/local/ssd/ai/projects/openwebui` | `/app/backend/data` | `127.0.0.1:3000 -> 8080/tcp`; SSH tunnel for remote access | Active documented / Disposable runtime | Keep; validate image tag and whether state remains disposable |
| Reverse proxy / Traefik | Needs validation | Traefik; image tag needs validation | `/opt/traefik`; compose file path needs validation | `/opt/traefik/config`, `/opt/traefik/dynamic`, `/opt/traefik/certs`, `/opt/traefik/logs`, `/opt/traefik/acme` | Needs validation | `:80`, `:443`, `:8443`; possible bootstrap `127.0.0.1:18080 -> 8080` | Active documented / Ansible candidate after compose inventory | Keep; validate compose file, image tag, container name, and dashboard exposure |

## Validated Media Stack Inventory

The following media stack state is validated for Milestone 9 and reconciled into service documentation. API-level media application wiring was configured and validated on 2026-05-16; indexer configuration and end-to-end download/import tests still need validation.

| Service / Stack | Container Name | Image | Compose Path | Host Data Paths | Container Paths | Ports / Exposure | Lifecycle Classification | Recommended Action |
|---|---|---|---|---|---|---|---|---|
| Gluetun | `gluetun` | `qmcgaw/gluetun:latest` | `/opt/vpn/docker-compose.yml` | `/opt/vpn/gluetun` | `/gluetun` | Publishes qBittorrent WebUI as `127.0.0.1:8080:8080` | Active documented / Persistent runtime config | Keep; preserve VPN boundary and secrets model |
| qBittorrent | `qbittorrent` | `lscr.io/linuxserver/qbittorrent:latest` | `/opt/vpn/docker-compose.yml` | `/opt/torrents/config`, `/opt/torrents/downloads` | `/config`, `/downloads` | `network_mode: service:gluetun`; WebUI localhost-only through Gluetun | Active documented / Local staging disposable | Keep; version `v5.1.4`, default save path `/downloads`, and categories `radarr`, `sonarr`, `mam`, `manual` validated |
| Prowlarr | `prowlarr` | `lscr.io/linuxserver/prowlarr:latest` | `/opt/vpn/docker-compose.yml` | `/opt/arr/prowlarr` | `/config` | `0.0.0.0:9696` temporary broad exposure | Active documented / Persistent runtime config | Keep; reduce exposure in future ingress/security pass |
| Radarr | `radarr` | `lscr.io/linuxserver/radarr:latest` | `/opt/vpn/docker-compose.yml` | `/opt/arr/radarr`, `/opt/torrents/downloads`, `/mnt/atlas/managed-media/movies` | `/config`, `/downloads`, `/movies` | `0.0.0.0:7878` temporary broad exposure | Active documented / Persistent runtime config with Atlas authoritative library | Keep; `SKIP_CHOWN=true`, root folder `/movies`, and qBittorrent category `radarr` validated |
| Sonarr | `sonarr` | `lscr.io/linuxserver/sonarr:latest` | `/opt/vpn/docker-compose.yml` | `/opt/arr/sonarr`, `/opt/torrents/downloads`, `/mnt/atlas/managed-media/tv` | `/config`, `/downloads`, `/tv` | `0.0.0.0:8989` temporary broad exposure | Active documented / Persistent runtime config with Atlas authoritative library | Keep; `SKIP_CHOWN=true`, root folder `/tv`, and qBittorrent category `sonarr` validated |

## Validated Atlas Media Mounts

| Atlas Export | Prometheus Mount | Status | Notes |
|---|---|---|---|
| `192.168.60.102:/mnt/user/managed-media` | `/mnt/atlas/managed-media` | Active | Authoritative managed media share. |
| `192.168.60.102:/mnt/user/shared-media` | `/mnt/atlas/shared-media` | Active | Authoritative shared media share. |
| `/mnt/atlas/downloads` | Not applicable | Not active | Not an active Atlas export; downloads remain local on Prometheus. |

## Requested Inventory Items Needing Validation

The following items are explicitly requested for this inventory, but current repository documentation does not prove their deployed state, compose paths, images, ports, or data paths.

| Service / Stack | Container Name | Image | Compose Path | Host Data Paths | Container Paths | Ports / Exposure | Lifecycle Classification | Recommended Action |
|---|---|---|---|---|---|---|---|---|
| Homelable | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Active needs validation | Inspect live Docker and add service documentation before cleanup |
| SearXNG | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Active needs validation | Track under issue #72; document before integration or cleanup |
| SearXNG Redis | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Active needs validation | Track with SearXNG; confirm whether Redis is dedicated or shared |
| Gluetun | See validated media stack inventory | `qmcgaw/gluetun:latest` | `/opt/vpn/docker-compose.yml` | `/opt/vpn/gluetun` | `/gluetun` | `127.0.0.1:8080:8080` for qBittorrent WebUI through Gluetun | Active documented | Original requested row reconciled above |
| qBittorrent | See validated media stack inventory | `lscr.io/linuxserver/qbittorrent:latest` | `/opt/vpn/docker-compose.yml` | `/opt/torrents/config`, `/opt/torrents/downloads` | `/config`, `/downloads` | Localhost-only through Gluetun | Active documented | Original requested row reconciled above; download transfer test still needs validation |
| Radarr | See validated media stack inventory | `lscr.io/linuxserver/radarr:latest` | `/opt/vpn/docker-compose.yml` | `/opt/arr/radarr`, Atlas movies, local downloads | `/config`, `/movies`, `/downloads` | `0.0.0.0:7878` temporary broad exposure | Active documented | Original requested row reconciled above; import test still needs validation |
| Sonarr | See validated media stack inventory | `lscr.io/linuxserver/sonarr:latest` | `/opt/vpn/docker-compose.yml` | `/opt/arr/sonarr`, Atlas TV, local downloads | `/config`, `/tv`, `/downloads` | `0.0.0.0:8989` temporary broad exposure | Active documented | Original requested row reconciled above; import test still needs validation |
| Prowlarr | See validated media stack inventory | `lscr.io/linuxserver/prowlarr:latest` | `/opt/vpn/docker-compose.yml` | `/opt/arr/prowlarr` | `/config` | `0.0.0.0:9696` temporary broad exposure | Active documented | Original requested row reconciled above; Radarr/Sonarr app links validated; indexers still need validation |
| Portainer | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Active needs validation | Confirm MGMT-only or localhost-only access before deployment/docs closeout |
| Jellyfin | Needs validation | Needs validation | Needs validation | Target mount `/mnt/atlas/managed-media:/media:ro` needs validation | `/media` target needs validation | Needs validation | Migration candidate / Needs validation | Do not mark deployed; confirm compose source, config path, library paths, and network exposure before deployment |

## Questionable / Exited Containers

These items are named in the issue scope but are not documented elsewhere in the repository.

| Service / Stack | Container Name | Image | Compose Path | Host Data Paths | Container Paths | Ports / Exposure | Lifecycle Classification | Recommended Action |
|---|---|---|---|---|---|---|---|---|
| Unknown | `anemoi` | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Questionable / exited needs validation | Inspect live Docker state; do not delete until owner and data paths are identified |
| Unknown | `gemma-192k` | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Questionable / exited needs validation | Inspect live Docker state; confirm whether this is model/runtime residue |
| Docker volumes | Anonymous Docker volumes | Needs validation | Not applicable | Needs validation | Needs validation | Not applicable | Cleanup candidate / Needs validation | Run read-only Docker volume inventory before pruning; do not delete from docs alone |

## Required Live Inventory Commands

Run these only when explicitly approved on Prometheus.

```bash
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
docker compose ls
docker volume ls
docker volume inspect $(docker volume ls -q)
find /opt -maxdepth 3 -name 'docker-compose.yml' -o -name 'compose.yml'
find ~/stacks -maxdepth 4 -name 'docker-compose.yml' -o -name 'compose.yml'
find /mnt/local -maxdepth 5 -name 'docker-compose.yml' -o -name 'compose.yml'
```

## Stop Points

- Do not delete containers from this inventory alone.
- Do not prune anonymous volumes until ownership is validated.
- Do not move stacks between `/opt`, `~/stacks`, and `/mnt/local` until compose files and data paths are mapped.
- Do not expose services while documenting inventory.
- Do not convert `Needs validation` rows into facts without repository evidence.
