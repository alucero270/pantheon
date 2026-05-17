# Prometheus Service Inventory

## Purpose

This document maps Prometheus service and container inventory before cleanup, migration, or stack normalization.

No services are deleted, moved, stopped, or modified by this inventory.

## Evidence Boundary

Use repository evidence and explicitly provided validated live state only.

Rows marked `Needs validation` identify services, containers, paths, ports, or images requested for inventory but not proven by the current repository documentation or validated live-state evidence.

Direct SSH revalidation from this workstation succeeded on 2026-05-16. The media stack rows below are reconciled from live Prometheus evidence and the validated state supplied for Milestone 9.

Direct SSH revalidation for the AI, Traefik, and SearXNG state succeeded on 2026-05-17. No services were stopped, moved, deleted, or modified during that run.

## Related Docs

- [[systems/prometheus]]
- [[systems/prometheus/architecture/compose-registry]]
- [[systems/prometheus/architecture/storage-authority-map]]
- [[decisions/ADR-010-container-lifecycle-policy-prometheus]]
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
| `/home/alex/stacks/ai/docker-compose.yml` | Validated live state on 2026-05-17, [[systems/prometheus/services/comfyui]] | AI Docker Compose stack location | Home-relative path; owner and backup posture need decision | Normalize only after standard layout and rollback are decided |
| `/mnt/local/nvme/ai/...` | [[systems/prometheus/procedures/ai-stack-initialization]], [[systems/prometheus/services/ollama]], [[systems/prometheus/services/comfyui]], [[systems/prometheus/services/llamacpp]], [[systems/prometheus/services/llama-swap]] | Fast local runtime/model/service data | Disposable local data, but still operationally important | Keep as local runtime path; validate ownership and mount state |
| `/mnt/local/ssd/ai/...` | [[systems/prometheus/procedures/ai-stack-initialization]], [[systems/prometheus/services/openwebui]], [[systems/prometheus/services/comfyui]] | Write-heavy local project/output data | Disposable local data; output handling needs validation | Keep as local runtime/output path; validate backup expectation |
| `/mnt/local/ssd/ai/services/searxng/docker-compose.yml` | Validated live state on 2026-05-17, [[systems/prometheus/services/searxng]] | SearXNG compose and config root | Compose source lives under local AI service data | Keep until standard layout and rollback are decided |

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
| AI stack | `comfy`, `ollama`, `openwebui`; exited `gemma-192k` | Mixed; see service rows | `/home/alex/stacks/ai/docker-compose.yml` | `/mnt/local/nvme/ai/`, `/mnt/local/ssd/ai/` | See service rows | Traefik routes for ComfyUI, OpenWebUI, and Ollama; Ollama route needs decision | Active documented / Needs access-model decision | Keep; resolve Ollama route drift before automation |
| ComfyUI | `comfy` | `mmartial/comfyui-nvidia-docker:latest` | `/home/alex/stacks/ai/docker-compose.yml` | `/mnt/local/nvme/ai/services/comfy-mnt`, `/mnt/local/nvme/ai/models`, `/mnt/local/ssd/ai/outputs/comfy` | `/comfy/mnt`, `/comfy/shared-models`, `/comfy/mnt/output` | Traefik route `comfy.home.arpa`; no host port | Active documented / Disposable runtime | Keep; preserve UID/GID 1024:1024 constraints |
| llama.cpp router | `llamacpp-router.service` | Native `llama-server` from `/mnt/local/nvme/ai/runtimes/llama-cpp-turboquant` | `/etc/systemd/system/llamacpp-router.service`; `/mnt/local/nvme/ai/profiles/start-scripts/llama-router.sh`; `/mnt/local/nvme/ai/profiles/llama-router-models.ini` | `/mnt/local/nvme/ai/runtimes`, `/mnt/local/nvme/ai/models/gguf`, `/mnt/local/nvme/ai/profiles` | Not containerized | `172.17.0.1:8084`; local API key | Active documented / Disposable runtime | Keep; `ik_llama.cpp` is available for MTP validation, while `llama-cpp-turboquant` is used for turbo KV cache profiles |
| llama-swap | `llama-swap.service` | Native `llama-swap` v214 | `/etc/systemd/system/llama-swap.service`; `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml` | `/mnt/local/nvme/ai/runtimes/llama-swap`, `/mnt/local/nvme/ai/runtimes/ik_llama.cpp`, `/mnt/local/nvme/ai/models/gguf` | Not containerized | `172.17.0.1:8085`; local API key | Active documented / Disposable runtime | Keep; no Traefik route documented; exposes one OpenWebUI-visible ID per profile; tested profiles include full-GPU Granite 30B at 80K and MoE CPU/GPU expert splits for GLM 4.6V and Qwen 122B |
| Ollama | `ollama` | `ollama/ollama:latest` | `/home/alex/stacks/ai/docker-compose.yml` | `/mnt/local/nvme/ai/services/ollama`, `/mnt/local/ssd/ai/modelfiles` | `/root/.ollama`, `/modelfiles` | `127.0.0.1:11434 -> 11434/tcp`; live Traefik route `ollama.home.arpa` needs decision | Active documented / Disposable runtime | Keep; decide whether to remove route or update ingress decision |
| OpenWebUI | `openwebui` | `ghcr.io/open-webui/open-webui:latest` | `/home/alex/stacks/ai/docker-compose.yml` | `/mnt/local/ssd/ai/projects/openwebui` | `/app/backend/data` | Traefik route `openwebui.home.arpa`; no host port | Active documented / Disposable runtime by current docs | Keep; Ollama and llama-swap are enabled; web search disabled in live environment |
| SearXNG | `searxng`, `searxng-redis` | `searxng/searxng:latest`, `redis:7-alpine` | `/mnt/local/ssd/ai/services/searxng/docker-compose.yml` | `/mnt/local/ssd/ai/services/searxng/searxng`; anonymous Docker volumes for cache and Redis data | `/etc/searxng`, `/var/cache/searxng`, `/data` | Traefik route `searxng.home.arpa`; no host port; IP allowlist label present | Active documented / Persistent runtime config | Keep; complete OpenWebUI integration and limiter validation under issue #72 |
| Reverse proxy / Traefik | `traefik` | `traefik:v3.6.1` | `/opt/traefik/docker-compose.yml` | `/opt/traefik/config`, `/opt/traefik/dynamic`, `/opt/traefik/certs`, `/opt/traefik/logs`, `/opt/traefik/acme` | `/traefik.yml`, `/dynamic`, `/certs`, `/logs`, `/acme` | `0.0.0.0:80`, `0.0.0.0:443`, `0.0.0.0:8443`, `127.0.0.1:18080 -> 8080` | Active documented / Persistent runtime config | Keep; dashboard exposure still depends on Cerberus MGMT-only policy |

## Validated AI Model Inventory

The following model inventory was collected from live Prometheus state on 2026-05-17.

### Ollama Models

Ollama model manifests and blobs live under `/mnt/local/nvme/ai/services/ollama/models`.

| Model | Size |
|---|---|
| `devstral-small-2:latest` | 15 GB |
| `qwen3.5:27b` | 17 GB |
| `dev-assist/glm-agent-16k:latest` | 17 GB |
| `huihui_ai/glm-4.7-flash-abliterated:q4_K_S` | 17 GB |
| `dev-assist/r1-architect:latest` | 17 GB |
| `dev-assist/qwen3-workhorse:latest` | 17 GB |
| `hf.co/bartowski/DeepSeek-R1-Distill-Qwen-32B-GGUF:IQ4_XS` | 17 GB |
| `hf.co/unsloth/Qwen3-32B-GGUF:IQ4_XS` | 17 GB |
| `gpt-oss:20b` | 13 GB |
| `dev-assist/mistral-general:latest` | 7.1 GB |
| `dev-assist/qwen35-workhorse:latest` | 17 GB |
| `dev-assist/qwen-thinking:latest` | 18 GB |
| `dev-assist/devstral-inline:latest` | 15 GB |
| `qwen3:30b-a3b-thinking-2507-q4_K_M` | 18 GB |
| `mistral-nemo:latest` | 7.1 GB |

### Shared GGUF Models

Shared GGUF models live under `/mnt/local/nvme/ai/models/gguf`.

| Model Path | Notes |
|---|---|
| `/mnt/local/nvme/ai/models/gguf/gemma-4-31b-it-iq4_xs/gemma-4-31B-it-IQ4_XS.gguf` | Used by exited `gemma-192k` llama.cpp-derived container; added to `llama-swap` as `gemma-4-31b-it` on 2026-05-17 |
| `/mnt/local/nvme/ai/models/gguf/qwen3.6-35b-a3b-mtp-unsloth-ud-iq4-xs/UD-IQ4_XS/Qwen3.6-35B-A3B-UD-IQ4_XS.gguf` | Installed for llama.cpp on 2026-05-17 |
| `/mnt/local/nvme/ai/models/gguf/qwen3.5-9b-mtp-unsloth-ud-q4-k-xl/UD-Q4_K_XL/Qwen3.5-9B-UD-Q4_K_XL.gguf` | Installed for llama.cpp on 2026-05-17; duplicate Ollama tag `qwen3.5:9b` removed |
| `/mnt/local/nvme/ai/models/gguf/qwen3.6-27b-mtp-unsloth-ud-q3-k-xl/UD-Q3_K_XL/Qwen3.6-27B-UD-Q3_K_XL.gguf` | Installed for llama.cpp on 2026-05-17 |
| `/mnt/local/nvme/ai/models/gguf/gemma-4-26b-a4b-it-unsloth-ud-iq4-xs/UD-IQ4_XS/gemma-4-26B-A4B-it-UD-IQ4_XS.gguf` | Installed for llama.cpp on 2026-05-17 |
| `/mnt/local/nvme/ai/models/gguf/qwen3.5-122b-a10b-unsloth-ud-iq4-xs/UD-IQ4_XS/` | Three-part GGUF set installed for llama.cpp on 2026-05-17 |
| `/mnt/local/nvme/ai/models/gguf/glm-4.6v-unsloth-ud-q3-k-xl/UD-Q3_K_XL/` | Two-part GGUF set installed for llama.cpp on 2026-05-17 |
| `/mnt/local/nvme/ai/models/gguf/glm-4.7-flash-unsloth-ud-q3-k-xl/UD-Q3_K_XL/GLM-4.7-Flash-UD-Q3_K_XL.gguf` | Installed for llama.cpp on 2026-05-17 |
| `/mnt/local/nvme/ai/models/gguf/granite-4.1-30b-unsloth-ud-q3-k-xl/UD-Q3_K_XL/granite-4.1-30b-UD-Q3_K_XL.gguf` | Installed for llama.cpp on 2026-05-17 |
| `/mnt/local/nvme/ai/models/gguf/granite-4.1-8b-unsloth-ud-q3-k-xl/UD-Q3_K_XL/granite-4.1-8b-UD-Q3_K_XL.gguf` | Installed for llama.cpp on 2026-05-17 |
| `/mnt/local/nvme/ai/models/gguf/minimax-m2-7-unsloth-ud-iq4-xs/UD-IQ4_XS/` | Four-part GGUF set |
| `/mnt/local/nvme/ai/models/gguf/nemotron-3-super-120b-a12b-unsloth-ud-q2-k-xl/UD-Q2_K_XL/` | Three-part GGUF set |
| `/mnt/local/nvme/ai/models/gguf/nemotron-3-super-120b-a12b-unsloth-ud-q3-k-xl/UD-Q3_K_XL/` | Three-part GGUF set |

### Modelfiles

Ollama Modelfiles live under `/mnt/local/ssd/ai/modelfiles`.

| File |
|---|
| `01-devstral-inline.Modelfile` |
| `02-qwen-workhorse.Modelfile` |
| `03-qwen-thinking.Modelfile` |
| `04-r1-debug.Modelfile` |
| `05-glm-agent-16k.Modelfile` |
| `06-glm-agent-32k-experimental.Modelfile` |
| `07-mistral-general.Modelfile` |
| `08-qwen35-workhorse.Modelfile` |
| `09-deepseek-r1-32b.Modelfile` |
| `deepseek-32b-stable.Modelfile` |
| `qwen3-30b-ui.Modelfile` |

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
| SearXNG | See active documented inventory | `searxng/searxng:latest` | `/mnt/local/ssd/ai/services/searxng/docker-compose.yml` | `/mnt/local/ssd/ai/services/searxng/searxng`; anonymous cache volume | `/etc/searxng`, `/var/cache/searxng` | Traefik route `searxng.home.arpa` | Active documented | Tracked under issue #72; OpenWebUI web search still disabled |
| SearXNG Redis | See active documented inventory | `redis:7-alpine` | `/mnt/local/ssd/ai/services/searxng/docker-compose.yml` | Anonymous Docker volume | `/data` | Docker networks only | Active documented | Dedicated to SearXNG |
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
