# Prometheus Storage Authority Map

## Purpose

This map classifies important Prometheus paths as authoritative, persistent runtime, disposable, or unknown.

Prometheus is disposable compute. Authoritative storage lives on [[systems/atlas]].

## Controlling Rules

- Prometheus is disposable compute: [[decisions/ADR-003-disposable-compute-prometheus]]
- Atlas is authoritative storage: [[decisions/ADR-002-atlas-as-storage]]
- Pantheon data strategy: [[systems/atlas/architecture/data-strategy]]

## Classification Model

| Classification | Meaning |
|---|---|
| Authoritative | Source of truth. Prometheus should not be authoritative without an ADR. |
| Persistent runtime | Service continuity data needed to restore a runtime, but not authoritative user data. |
| Disposable | Rebuildable cache/output/local runtime data that may be recreated. |
| Unknown / Needs validation | Path is known or requested, but repo evidence is not enough to classify safely. |

## Prometheus Paths

| Path | Purpose | Used By | Authority Classification | Backup Requirement | Migration Notes |
|---|---|---|---|---|---|
| `/mnt/local/nvme/ai/services` | Parent for AI service runtime data | AI stack | Disposable / Persistent runtime by service | No authoritative backup; validate service-specific recovery needs | Keep local unless reclassified by ADR |
| `/mnt/local/nvme/ai/services/comfy-mnt` | Required ComfyUI runtime/state mount | [[systems/prometheus/services/comfyui]] | Disposable | No authoritative backup; validate generated output handling | Preserve UID/GID 1024:1024 if migrated |
| `/mnt/local/nvme/ai/services/ollama` | Ollama state and downloaded models | [[systems/prometheus/services/ollama]] | Disposable | No authoritative backup by current docs; re-pull acceptable | Validate if any model becomes expensive to reproduce |
| `/mnt/local/nvme/ai/models` | Shared AI models | AI stack, ComfyUI | Disposable / Needs validation | No authoritative backup unless promoted by decision | Validate whether this is cache, curated model store, or reproducible download set |
| `/mnt/local/nvme/ai/runtimes` | Requested path; no current repo evidence found | Unknown | Unknown / Needs validation | Needs validation | Inspect before cleanup or migration |
| `/mnt/local/ssd/ai/projects` | Parent for AI project/runtime state | AI stack | Persistent runtime / Disposable by service | Needs validation | Keep local until ownership and backup stance are decided |
| `/mnt/local/ssd/ai/projects/openwebui` | OpenWebUI app state | [[systems/prometheus/services/openwebui]] | Disposable by current docs | Not backed up by current docs | Revisit if OpenWebUI becomes multi-user or production-facing |
| `/mnt/local/ssd/ai/modelfiles` | Ollama Modelfile workspace | [[systems/prometheus/procedures/ollama-model-management]] | Persistent runtime / Needs validation | Needs validation | Candidate for Git-backed source if curated |
| `/mnt/local/ssd/ai/outputs` | Parent for generated AI outputs | AI stack | Disposable / Needs validation | Needs validation | Promote important outputs to Atlas before treating them as authoritative |
| `/mnt/local/ssd/ai/outputs/comfy` | ComfyUI generated outputs | [[systems/prometheus/services/comfyui]] | Disposable / Needs validation | Needs validation | Move important outputs to Atlas before cleanup |
| `/opt/traefik` | Reverse proxy deployment/config root | [[systems/prometheus/services/traefik]] | Persistent runtime / Config | Back up config/dynamic/certs if self-signed is long-term | Keep until compose/config source of truth is validated |
| `/opt/vpn` | Live VPN/media egress stack root | [[systems/prometheus/services/gluetun]] | Persistent runtime / Service config | Back up sanitized config only; secrets recovery needs validation | Live compose path is `/opt/vpn/docker-compose.yml`; do not commit VPN secrets |
| `/opt/vpn/gluetun` | Gluetun runtime config | [[systems/prometheus/services/gluetun]] | Persistent runtime / Service config | Needs validation | Preserve secrets boundary |
| `/opt/arr` | Media automation config parent | Prowlarr, Radarr, Sonarr | Persistent runtime / Service config | Needs validation | Config/database state for Arr services |
| `/opt/arr/prowlarr` | Prowlarr config | [[systems/prometheus/services/prowlarr]] | Persistent runtime / Service config | Needs validation | API keys must stay outside Git |
| `/opt/arr/radarr` | Radarr config | [[systems/prometheus/services/radarr]] | Persistent runtime / Service config | Needs validation | Atlas movie library is authoritative, not this config path |
| `/opt/arr/sonarr` | Sonarr config | [[systems/prometheus/services/sonarr]] | Persistent runtime / Service config | Needs validation | Atlas TV library is authoritative, not this config path |
| `/opt/torrents` | qBittorrent config and download staging parent | [[systems/prometheus/services/qbittorrent]] | Mixed persistent runtime and disposable staging | Config backup needs validation; downloads are disposable | Downloads must remain local staging unless an ADR changes authority |
| `/opt/torrents/config` | qBittorrent config | [[systems/prometheus/services/qbittorrent]] | Persistent runtime / Service config | Needs validation | WebUI credentials must stay outside Git |
| `/opt/torrents/downloads` | qBittorrent download staging | qBittorrent, Radarr, Sonarr | Disposable / Prometheus-local staging | No authoritative backup | Container path `/downloads`; categories `radarr` and `sonarr` |
| `/opt/media-staging` | Requested media staging path | Media workflow candidate | Unknown / Needs validation | Needs validation | Staging must not become authoritative unless promoted to Atlas |
| `/mnt/atlas/managed-media` | Active Atlas NFS mount | Media automation and future Jellyfin | Atlas authoritative mount | Atlas backup/storage policy applies | Export `192.168.60.102:/mnt/user/managed-media`; final media libraries live here |
| `/mnt/atlas/managed-media/movies` | Final movie library | [[systems/prometheus/services/radarr]] | Authoritative on Atlas | Atlas backup/storage policy applies | Container path `/movies`; Radarr writes final movie library |
| `/mnt/atlas/managed-media/tv` | Final TV library | [[systems/prometheus/services/sonarr]] | Authoritative on Atlas | Atlas backup/storage policy applies | Container path `/tv`; Sonarr writes final TV library |
| `/mnt/atlas/shared-media` | Active Atlas NFS mount | Shared media workflows | Authoritative on Atlas | Atlas backup/storage policy applies | Export `192.168.60.102:/mnt/user/shared-media` |
| `/mnt/atlas/downloads` | Non-active Atlas download path | None | Not active / Not authoritative | Not applicable | Not an active Atlas export; do not use for qBittorrent downloads |

## Migration Rules

- Do not treat any Prometheus local path as authoritative without an ADR.
- Promote important Prometheus outputs to Atlas before considering them authoritative.
- Do not prune or migrate unknown paths until ownership and data role are validated.
