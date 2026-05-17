---
type: service
service_name: openwebui
status: active
last_updated: 2026-05-17
---

# OpenWebUI

## Purpose

OpenWebUI provides the primary human-facing UI for interacting with local LLMs hosted by [[systems/prometheus/services/ollama]] and [[systems/prometheus/services/llama-swap]] on [[systems/prometheus]].

It is used for:

- interactive chat and prompt experimentation
- UX evaluation of model behavior
- validation of model tuning, latency, context, and VRAM behavior
- early validation of local tool and search integrations

OpenWebUI is not authoritative storage.

## Hosting

- System: [[systems/prometheus]]
- Runtime: Docker container (`openwebui`)
- Image: `ghcr.io/open-webui/open-webui:latest`
- Compose path: `/home/alex/stacks/ai/docker-compose.yml`
- Dependency: [[systems/prometheus/services/ollama]], [[systems/prometheus/services/llama-swap]]

## Network & Access

Live state observed on 2026-05-17:

- Container port: `8080/tcp`
- No host port is published.
- The container joins the `proxy` Docker network.
- Traefik route: `https://openwebui.home.arpa`
- Traefik service target: container port `8080`

OpenWebUI is no longer localhost-only in live state. It is exposed through [[systems/prometheus/services/traefik]] using Docker labels.

## Data Classification

- Authoritative: no
- Runtime: yes
- Disposable: yes by current docs

All OpenWebUI state is treated as disposable compute data unless a later decision promotes it to persistent service state.

## Storage Paths

| Path | Read/Write | Description |
|---|---|---|
| `/mnt/local/ssd/ai/projects/openwebui` | RW | App state, users, chats, settings, uploads, cache, and vector DB |

Mounted into the container as `/app/backend/data`.

## Configuration

Live environment highlights:

- `ENABLE_OLLAMA_API=true`
- `OLLAMA_BASE_URL=http://ollama:11434`
- `ENABLE_OPENAI_API=true`
- `OPENAI_API_BASE_URLS=http://host.docker.internal:8085/v1`
- `OPENAI_API_KEYS=LOCAL`
- `ENABLE_WEB_SEARCH=false`
- `ENABLE_RETRIEVAL=false`

The live OpenWebUI database config was reconciled on 2026-05-17 so Ollama is enabled through `http://ollama:11434` and the OpenAI-compatible local endpoint points at [[systems/prometheus/services/llama-swap]] on `http://host.docker.internal:8085/v1`.

The current SearXNG service is documented at [[systems/prometheus/services/searxng]]. OpenWebUI web search is not enabled in live state as of 2026-05-17.

Read-only validation from inside the OpenWebUI container confirmed that `http://searxng:8080/search?q=test&format=json` returns JSON. The HTTPS Traefik URL fails from inside OpenWebUI because the current internal certificate is self-signed and not trusted by the container.

## Security Notes

- OpenWebUI is reachable through Traefik at `openwebui.home.arpa`.
- Authentication is handled internally by OpenWebUI.
- Access policy depends on DNS, Traefik routing, and Cerberus firewall policy.
- Service state may include user/chat data; keep secrets and exports out of Git.

## Backup Strategy

- Backed up: no
- Rationale: treated as disposable runtime under current docs.
- Revisit if OpenWebUI becomes multi-user, production-facing, or contains important chat/workflow history.

## Monitoring & Health

Container state:

```bash
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | grep -E "^openwebui\b"
```

Ingress validation from Prometheus:

```bash
curl -k --resolve openwebui.home.arpa:443:127.0.0.1 https://openwebui.home.arpa/
```

## Upgrade Strategy

- Update the container image and redeploy the AI compose stack.
- Current image tag is floating `latest`; pinning known-good versions is tracked separately by issue #63.

## Known Issues

- OpenWebUI web search is disabled in live state.
- SearXNG is reachable over Docker DNS, but OpenWebUI is not configured to use it yet.
- OpenWebUI now uses [[systems/prometheus/services/llama-swap]] for OpenAI-compatible llama.cpp model tests and [[systems/prometheus/services/ollama]] for Ollama-hosted models. Direct `llamacpp-router.service` testing on `8084` may not match the tuned `llama-swap` model profiles.
- OpenWebUI may surface errors that originate from Ollama model load failures, VRAM allocation failures, request shape, model switching, keepalive behavior, or concurrency.

## Related Docs

- Services: [[systems/prometheus/services/ollama]], [[systems/prometheus/services/llama-swap]], [[systems/prometheus/services/comfyui]], [[systems/prometheus/services/searxng]], [[systems/prometheus/services/traefik]]
- Procedures: [[systems/prometheus/procedures/ai-stack-initialization]], [[systems/prometheus/procedures/searxng-openwebui-integration]]
- Architecture: [[systems/prometheus/architecture/storage-authority-map]], [[systems/prometheus/architecture/compose-registry]]

## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Prometheus |
| Host/system/device owner | Prometheus |
| Runtime type | Docker web UI |
| Source of truth | `/home/alex/stacks/ai/docker-compose.yml`; documentation reconciliation tracked by issue #84 |
| Config path | `/mnt/local/ssd/ai/projects/openwebui` |
| Data path | `/mnt/local/ssd/ai/projects/openwebui` |
| Secret requirements | Do not commit secrets, API keys, exports, or user data |
| Network ports | Container `8080/tcp`; Traefik route `openwebui.home.arpa`; no host port |
| Dependencies | [[systems/prometheus/services/ollama]], [[systems/prometheus/services/llama-swap]], Docker, [[systems/prometheus/services/traefik]] |
| Backup requirement | No current backup; revisit if service state becomes important |
| Validation command | `curl -k --resolve openwebui.home.arpa:443:127.0.0.1 https://openwebui.home.arpa/` |
| Recovery procedure | [[systems/prometheus/procedures/ai-stack-initialization]] |
| Automation classification | Ansible candidate after compose and secrets handling are normalized |
| Preferred automation tool | Ansible |
