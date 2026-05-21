# Docker Compose Registry

## Purpose

This registry documents known Docker Compose stack locations on Prometheus before cleanup, migration, or stack normalization.

This document does not move files, delete services, prune volumes, or modify live infrastructure.

## Evidence Boundary

Use repository evidence and explicitly provided validated live state only.

Some compose paths in this registry are user-reported current-state candidates from the issue that requested this document. Those paths are marked `Needs validation` until confirmed by repository documentation, validated live-state evidence, or a read-only inventory run on Prometheus.

Direct SSH revalidation from this workstation succeeded on 2026-05-16. The media stack row is reconciled from live Prometheus evidence and validated live-state evidence supplied for Milestone 9.

## Related Docs

- [[systems/prometheus]]
- [[systems/prometheus/inventory]]
- [[decisions/ADR-010-container-lifecycle-policy-prometheus]]
- [[systems/prometheus/services/README]]
- [[systems/prometheus/opt/stacks/ai/core/procedures/ai-stack-initialization]]
- [[systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy]]
- [[automation/policies/automation-classification]]

## Standard Layout Status

The final standard layout for Prometheus compose files is `Needs decision`.

Current documentation shows compose and service state split across:

- `/opt/...`
- `~/stacks/...`
- `/home/alex/stacks/...`
- `/mnt/local/...`

Do not move stacks until:

- each compose file is confirmed
- each container and volume is mapped
- host and container data paths are documented
- rollback steps exist
- ownership of the standard layout is decided

## Compose Registry

| Stack Name | Compose Path | Services | Owner / System | Status | Startup Priority | Standard Layout Action | Notes |
|---|---|---|---|---|---|---|---|
| AI stack | `/home/alex/stacks/ai/docker-compose.yml` | ComfyUI, Ollama, OpenWebUI; `gemma-192k` is an exited llama.cpp-derived service from the same compose project | [[systems/prometheus|Prometheus]] | Active documented from live validation on 2026-05-17 | Medium | Candidate to move after standard layout decision | Live compose uses Traefik labels for ComfyUI, OpenWebUI, and Ollama. Ollama route needs decision because ADR-007 says it remains internal-only. |
| Reverse proxy | `/opt/traefik/docker-compose.yml` | Traefik | [[systems/prometheus|Prometheus]] | Active documented from live validation on 2026-05-17 | High | Keep or standardize after ingress rollback is proven | Live image `traefik:v3.6.1`; ports `80`, `443`, `8443`, and localhost `18080 -> 8080`. |
| Homelable | `/opt/homelable/docker-compose.yml` | Backend, frontend, MCP | [[systems/prometheus|Prometheus]] | Active documented from live validation on 2026-05-18 | Low | Keep in place; service doc exists | Live build v1.13.0 from source; see [[systems/prometheus/opt/stacks/homelable/homelable]] |
| SearXNG | `/mnt/local/ssd/ai/services/searxng/docker-compose.yml` | SearXNG, Redis | [[systems/prometheus|Prometheus]] | Active documented from live validation on 2026-05-17 | Medium | Candidate to move after AI/search stack layout is decided | Dedicated Redis container `searxng-redis`; Traefik route `searxng.home.arpa`; tracked by issue #72. |
| VPN / media egress | `/opt/vpn/docker-compose.yml` | Gluetun, qBittorrent, Prowlarr, Radarr, Sonarr | [[systems/prometheus|Prometheus]] | Active documented from validated live state | Medium | Keep in place until standard layout decision and recovery procedure exist | Live media compose path. Secrets stay outside Git. qBittorrent is localhost-only through Gluetun; Prowlarr/Radarr/Sonarr broad binds are temporary current state. |
| Jellyfin | Needs validation | Jellyfin | [[systems/prometheus|Prometheus]] | Needs validation | Medium | Candidate to move after media inventory is validated | Repo does not yet prove live compose path on Prometheus. Track service doc at [[systems/prometheus/opt/stacks/media/jellyfin/jellyfin]]. |
| Anemoi | `/home/alex/stacks/ai/anemoi/deploy/docker/docker-compose.yml` | `anemoi`; related containers need validation | [[systems/prometheus|Prometheus]] | Questionable / exited needs validation | Low | Cleanup candidate after ownership and data paths are validated | User-reported compose path; do not delete until live container and volume ownership are known. |

## Artifact Paths

Compose files found inside Docker/containerd runtime storage are artifacts, not active source of truth.

| Path Pattern | Classification | Action |
|---|---|---|
| Docker overlay paths | Artifact | Do not treat as active compose source. Do not edit. Do not migrate from these paths. |
| containerd snapshot paths | Artifact | Do not treat as active compose source. Do not edit. Do not migrate from these paths. |
| anonymous volume mount contents | Needs validation | Inspect ownership before pruning or migration. |

## Startup Priority Model

| Priority | Meaning |
|---|---|
| High | Core ingress or dependency needed before other services are reachable |
| Medium | User-facing or workload service that depends on validated host/runtime state |
| Low | Experimental, questionable, exited, or cleanup-candidate stack |
| Needs validation | Repo does not prove startup dependency order |

## Standardization Candidates

| Stack | Should Move? | Reason | Required Before Move |
|---|---|---|---|
| AI stack | Needs decision | Current path is home-relative and may not be ideal for automation | Resolve Ollama route drift, standard layout, owner, data paths, and rollback |
| Reverse proxy | Needs decision | `/opt/traefik` may be appropriate for ingress | Confirm backup/restore process |
| Homelable | Active documented | Service doc created on 2026-05-18 from live validation ([systems/prometheus/opt/stacks/homelable/homelable]] | Resolve Traefik route and rotate default secrets |
| SearXNG | Needs decision | Path is under local AI service data; may mix compose source with runtime data | Complete service/procedure docs, OpenWebUI integration validation, and rollback |
| VPN / media egress | Needs decision | Live path is validated, but standard layout and recovery procedure are not finalized | Keep `/opt/vpn/docker-compose.yml` for now; document VPN boundary, media paths, secrets handling, and rollback before any move |
| Anemoi | Cleanup candidate | Requested as questionable/exited | Validate owner, data paths, and whether it is still needed |

## Read-Only Validation Commands

Run these only when explicitly approved on Prometheus.

```bash
docker compose ls
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
find /opt -maxdepth 3 -name 'docker-compose.yml' -o -name 'compose.yml'
find ~/stacks -maxdepth 5 -name 'docker-compose.yml' -o -name 'compose.yml'
find /home/alex/stacks -maxdepth 8 -name 'docker-compose.yml' -o -name 'compose.yml'
find /mnt/local -maxdepth 8 -name 'docker-compose.yml' -o -name 'compose.yml'
```

## Stop Points

- Do not move compose files from this registry alone.
- Do not edit compose files found in overlay or snapshot paths.
- Do not prune anonymous volumes until ownership is known.
- Do not standardize stack layout until the standard layout is decided.
- Do not convert user-reported paths into confirmed facts without validation.
