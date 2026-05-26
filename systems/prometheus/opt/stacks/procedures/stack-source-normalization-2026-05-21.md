# Prometheus Stack Source Normalization - 2026-05-21

## Purpose

Document the live normalization pass that moved Prometheus Docker Compose source files into `/opt/stacks` while preserving current runtime data paths and legacy operator entrypoints.

This procedure supports issue #112.

## Scope

Owning system: [[systems/prometheus]]

Live host: `prometheus`

Approved live work: normalize Compose source paths and validate services after the move.

Out of scope:

- Docker data-root migration from `/mnt/local/nvme/docker`
- containerd root migration
- volume pruning
- service rebuilds
- secret rotation
- Atlas storage changes

## Dependency Map

| Stack | Normalized compose source | Legacy compatibility path | Runtime/data dependencies | Validation status |
|---|---|---|---|---|
| AI core | `/opt/stacks/ai/core/compose.yml` | `/home/alex/stacks/ai/docker-compose.yml` symlink | `/mnt/local/nvme/ai/services/ollama`, `/mnt/local/nvme/ai/services/comfy-mnt`, `/mnt/local/nvme/ai/models`, `/mnt/local/ssd/ai/projects/openwebui`, `/mnt/local/ssd/ai/outputs/comfy`, Traefik `proxy` network | Compose config valid; OpenWebUI and Ollama responded; `comfy` was already exited before the move |
| SearXNG | `/opt/stacks/ai/searxng/compose.yml` | `/mnt/local/ssd/ai/services/searxng/docker-compose.yml` symlink | `/mnt/local/ssd/ai/services/searxng/searxng`, `.env` symlink to live secret file, `proxy` network, `ai_ai_internal` network | Compose config valid; SearXNG responded through Traefik |
| Voice agent | `/opt/stacks/ai/voice-agent/compose.yml` | `/home/alex/stacks/voice-agent/compose.yml` symlink | `.env` required for live Docker deployment; current installed validation runtime is Python-based under `/home/alex/stacks/voice-agent` | Example compose config valid using `.env.example`; live Docker stack not running |
| Traefik | `/opt/stacks/ingress/traefik/compose.yml` | `/opt/traefik/docker-compose.yml` symlink | `/opt/traefik/config`, `/opt/traefik/dynamic`, `/opt/traefik/certs`, `/opt/traefik/logs`, `/opt/traefik/acme`, Docker socket, `proxy` network | Compose config valid; routed services responded; dashboard localhost port did not respond and remains Needs validation |
| Media VPN | `/opt/stacks/media/vpn/compose.yml` | `/opt/vpn/docker-compose.yml` symlink | `/opt/vpn/.env`, `/opt/vpn/gluetun`, `/opt/torrents/config`, `/opt/torrents/downloads`, `/opt/arr`, `/mnt/atlas/managed-media` | Compose config valid with sudo due protected `.env`; Gluetun, qBittorrent, Prowlarr, Radarr, and Sonarr responded |
| Homelable | `/opt/stacks/homelable/compose.yml` | `/opt/homelable/docker-compose.yml` symlink | `/opt/homelable` source tree, `/opt/homelable/.env`, Docker volume `homelable_backend_data` | Compose config valid; frontend responded; MCP returned expected auth-gated `401`; backend container healthy |

## Live Changes

For each moved compose file:

1. Created a timestamped backup beside the original live file.
2. Wrote the normalized compose file under `/opt/stacks`.
3. Preserved the legacy path as a symlink to the normalized file.
4. Added an explicit Compose project `name` where needed to preserve project identity.
5. Changed only relative source references that would break after the move:
   - Homelable build contexts now point at `/opt/homelable`.
   - Homelable `env_file` now points at `/opt/homelable/.env`.
   - SearXNG config bind now points at `/mnt/local/ssd/ai/services/searxng/searxng`.
   - Media and SearXNG `.env` access is preserved through symlinks from the normalized stack folder to the existing live secret file.

No containers were intentionally recreated, restarted, deleted, or pruned during this pass.

## Rollback

Rollback is per stack.

```bash
sudo rm /legacy/compose/path
sudo mv /legacy/compose/path.TIMESTAMP.legacy /legacy/compose/path
```

If the normalized file was changed after the move, preserve it before rollback:

```bash
sudo cp /opt/stacks/<area>/<stack>/compose.yml /opt/stacks/<area>/<stack>/compose.yml.rollback-review.TIMESTAMP
```

Then validate from the restored legacy path:

```bash
docker compose -f /legacy/compose/path config -q
docker compose -f /legacy/compose/path ps
```

Use sudo for the media VPN stack because `/opt/vpn/.env` is intentionally protected.

## Validation Commands

```bash
docker compose -f /opt/stacks/ai/core/compose.yml config -q
docker compose -f /opt/stacks/ai/core/compose.yml ps
docker compose -f /opt/stacks/ai/searxng/compose.yml config -q
docker compose -f /opt/stacks/ai/searxng/compose.yml ps
docker compose -f /opt/stacks/ingress/traefik/compose.yml config -q
docker compose -f /opt/stacks/ingress/traefik/compose.yml ps
docker compose -f /opt/stacks/homelable/compose.yml config -q
docker compose -f /opt/stacks/homelable/compose.yml ps
sudo docker compose -f /opt/stacks/media/vpn/compose.yml config -q
sudo docker compose -f /opt/stacks/media/vpn/compose.yml ps
docker compose -f /opt/stacks/ai/voice-agent/compose.yml --env-file /home/alex/stacks/voice-agent/.env.example config -q
```

Service smoke checks used local curls against routed or localhost endpoints. HTTP `200`, redirect, or expected auth-gated status counted as service-responsive according to the service type.

## Remaining Needs Validation

- Decide whether and when Docker data-root should move from `/mnt/local/nvme/docker` to `/mnt/local/ssd/container-runtime/docker`.
- Validate whether `/opt/containerd` is package-managed, manually installed, or stale.
- Validate Traefik dashboard localhost access on `127.0.0.1:18080`.
- Decide whether the voice-agent Docker compose file is future scaffolding or should become the active runtime.
- Do not remove legacy symlinks until operator workflows and automation have been updated.

## Related Docs

- [[systems/prometheus/architecture/compose-registry]]
- [[systems/prometheus/inventory]]
- [[systems/prometheus/mnt/local/nvme/docker]]
- [[systems/prometheus/mnt/local/ssd/container-runtime]]
- [[systems/prometheus/opt/stacks/procedures/config-versioning-and-restore]]
- [[decisions/ADR-010-container-lifecycle-policy-prometheus]]
