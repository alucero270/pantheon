# Docker Compose Registry

## Purpose

This registry documents known Docker Compose stack locations on Prometheus before cleanup, migration, or stack normalization.

This document does not move files, delete services, prune volumes, or modify live infrastructure.

## Evidence Boundary

Use repository evidence only.

Some compose paths in this registry are user-reported current-state candidates from the issue that requested this document. Those paths are marked `Needs validation` until confirmed by repository documentation or a read-only inventory run on Prometheus.

## Related Docs

- [[systems/prometheus]]
- [[systems/prometheus/inventory]]
- [[architecture/container-lifecycle-policy]]
- [[systems/prometheus/services/README]]
- [[systems/prometheus/procedures/ai-stack-initialization]]
- [[systems/prometheus/procedures/reverse-proxy]]
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
| AI stack | `~/stacks/ai/docker-compose.yml` | ComfyUI, Ollama, OpenWebUI | [[systems/prometheus|Prometheus]] | Documented for ComfyUI; full stack needs validation | Medium | Candidate to move after standard layout decision | Repo documents this path in [[systems/prometheus/services/comfyui]]. Validate whether Ollama and OpenWebUI use the same compose file. |
| Reverse proxy | `/opt/traefik/docker-compose.yml` | Traefik | [[systems/prometheus|Prometheus]] | Needs validation | High | Keep or standardize after ingress rollback is proven | Repo documents `/opt/traefik` as deploy path, but the exact compose file path needs validation. |
| Homelable | `/opt/homelable/docker-compose.yml` | Needs validation | [[systems/prometheus|Prometheus]] | Needs validation | Needs validation | Candidate to move after service ownership is documented | User-reported compose path; no current repo service doc found. |
| SearXNG | `/mnt/local/ssd/ai/services/searxng/docker-compose.yml` | SearXNG, Redis | [[systems/prometheus|Prometheus]] | Needs validation | Medium | Candidate to move after AI/search stack layout is decided | User-reported compose path; tracked by issue #72. Confirm whether Redis is dedicated to SearXNG. |
| VPN / media egress | `/opt/vpn/docker-compose.yml` | Gluetun, qBittorrent, Radarr, Sonarr, Prowlarr | [[systems/prometheus|Prometheus]] | Needs validation | Medium | Candidate to move after media stack and VPN boundary are documented | User-reported compose path; document secrets, VPN dependency, media paths, and exposure before changes. |
| Jellyfin | Needs validation | Jellyfin | [[systems/prometheus|Prometheus]] | Needs validation | Medium | Candidate to move after media inventory is validated | Repo does not yet prove live compose path on Prometheus. Track service doc at [[systems/prometheus/services/jellyfin]]. |
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
| AI stack | Needs decision | Current path is home-relative and may not be ideal for automation | Confirm compose contents, owner, data paths, and rollback |
| Reverse proxy | Needs decision | `/opt/traefik` may be appropriate for ingress, but exact compose source needs validation | Confirm compose file path and backup/restore process |
| Homelable | Needs validation | No repo evidence of service ownership yet | Create service doc and validate live stack |
| SearXNG | Needs decision | Path is under local AI service data; may mix compose source with runtime data | Create service/procedure docs and validate Redis relationship |
| VPN / media egress | Needs decision | VPN/media stack should align with media milestone and secrets policy | Document VPN boundary, media paths, and secrets handling |
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
