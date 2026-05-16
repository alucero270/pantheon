# Prometheus Service Inventory

## Purpose

This document maps Prometheus service and container inventory before cleanup, migration, or stack normalization.

No services are deleted, moved, stopped, or modified by this inventory.

## Evidence Boundary

Use repository evidence only.

Rows marked `Needs validation` identify services, containers, paths, ports, or images requested for inventory but not proven by the current repository documentation.

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

## Requested Inventory Items Needing Validation

The following items are explicitly requested for this inventory, but current repository documentation does not prove their deployed state, compose paths, images, ports, or data paths.

| Service / Stack | Container Name | Image | Compose Path | Host Data Paths | Container Paths | Ports / Exposure | Lifecycle Classification | Recommended Action |
|---|---|---|---|---|---|---|---|---|
| Homelable | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Active needs validation | Inspect live Docker and add service documentation before cleanup |
| SearXNG | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Active needs validation | Track under issue #72; document before integration or cleanup |
| SearXNG Redis | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Active needs validation | Track with SearXNG; confirm whether Redis is dedicated or shared |
| Gluetun | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Active needs validation | Document VPN boundary, secrets model, and network exposure before changes |
| qBittorrent | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Active needs validation | Document data paths and VPN dependency before changes |
| Radarr | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Active needs validation | Document media paths and Atlas relationship before changes |
| Sonarr | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Active needs validation | Document media paths and Atlas relationship before changes |
| Prowlarr | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Active needs validation | Document indexer configuration and secret requirements before changes |
| Portainer | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Active needs validation | Confirm MGMT-only or localhost-only access before deployment/docs closeout |
| Jellyfin | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Active needs validation | Document compose source, library paths on Atlas, and network exposure before migration |

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
