---
type: service
service_name: anemoi-governance
status: active
last_updated: 2026-05-29
---

# Anemoi Governance Layer (Live Integration)

## Purpose

Anemoi provides inference governance for heterogeneous AI systems. It sits between the request surface and the model runtimes, making deterministic scheduling decisions based on residency state, latency budgets, and policy constraints.

This document covers the **live integration** with LlamaSwap running behind the Traefik reverse proxy.

## Hosting

- System: Prometheus (Ubuntu)
- Container / VM: Docker container (Anemoi daemon)
- Runtime: Rust binary (cargo run -p anemoi-daemon)
- Deploy path: `/home/alex/stacks/ai/anemoi`
- Config path: `config/anemoi.live.yaml`

## Data Classification

- Authoritative: none
- Runtime: governance decisions, telemetry, decision logs
- Disposable: the host (Prometheus) is rebuildable; all config must live in Git

## Storage Paths

| Path | Read/Write | Description |
|---|---|---|
| `config/anemoi.live.yaml` | R | Live Anemoi configuration with LlamaSwap roster |
| `/tmp/anemoi.db` | RW | Decision log (SQLite) |

## Configuration

- Config: `config/anemoi.live.yaml`
- Profile: live (points to real LlamaSwap via Traefik proxy)

### Routing Topology

All inference traffic routes through the Traefik reverse proxy:

```
[Client] → Traefik (anemoi.home.arpa:443)
           → Anemoi Daemon (127.0.0.1:7070)
              → LlamaSwap Adapter
                 → Traefik (llama-swap.home.arpa:443)
                    → LlamaSwap Container (8085)
                       → GPU Runtime
```

**Key URLs:**
- Anemoi API: `https://anemoi.home.arpa` (port 7070 behind Traefik)
- LlamaSwap API: `https://llama-swap.home.arpa` (port 8085 behind Traefik)
- Auth: `Authorization: Bearer LOCAL`

### Supported Models (LlamaSwap Roster)

**Fast / Interactive (small_swarm residency group):**
| Model | Family | Params | Context | VRAM | Cold Load |
|---|---|---|---|---|---|
| qwen3.5-9b | qwen | 9b | 32K | 9 GB | 18s |
| qwen3.5-9b-gpu | qwen | 9b | 32K | 9 GB | 15s |
| granite-4.1-8b | granite | 8b | 8K | 8 GB | 15s |
| granite-4.1-8b-gpu | granite | 8b | 8K | 8 GB | 12s |
| gemma-4-26b-a4b-it | gemma | 26b | 32K | 18 GB | 50s |

**Heavy / Quality (large_models residency group):**
| Model | Family | Params | Context | VRAM | Cold Load |
|---|---|---|---|---|---|
| qwen3.6-35b-a3b-mtp | qwen | 35b | 32K | 30 GB | 45s |
| qwen3.6-35b-a3b-mtp-co | qwen | 35b | 32K | 30 GB | 45s |
| qwen3.5-122b-a10b-mtp | qwen | 122b | 32K | 140 GB | 120s |
| nemotron-udiq4-256k | nemotron | 120b | 256K | 180 GB | 90s |

**Additional models (available via LlamaSwap, not in policy groups):**
- gemma-4-26b-a4b-it-mtp (Gemma 26B + MTP)
- gemma-4-26b-a4b-it-mtp-co (Gemma 26B MTP co-located)
- gemma-4-31b-it (Gemma 31B)
- gemma-4-31b-it-mtp (Gemma 31B + MTP)
- granite-4.1-30b (Granite 30B)
- glm-4.6v (GLM 4.6V)
- glm-4.7-flash (GLM 4.7 Flash)
- minimax-256k (MiniMax M2.7, 196K context)
- minimax-256k-iq3s (MiniMax M2.7, 128K context)

## Access

Internal governance API:
- [https://anemoi.home.arpa](https://anemoi.home.arpa) (443 via Traefik)

Endpoints:
- `GET /health` → Health check
- `POST /decide` → Make a scheduling decision (body: InferenceRequest)
- `POST /execute` → Decide + handoff to runtime
- `GET /status` → Operator status view
- `GET /residents` → Runtime snapshots
- `GET /explain/{decision_id}` → Decision explanation

## Security Notes

- Anemoi is behind Traefik with IP whitelist middleware (same as LlamaSwap)
- No secrets are committed; auth token originates from environment
- Governance decisions never touch model execution internals
- Live execution requires explicit opt-in via `ANEMOI_ENABLE_LIVE_EXECUTE=1`

## Monitoring & Health

Health checks:
- Container running: `docker ps | grep anemoi`
- API health: `curl -s http://anemoi.home.arpa/health`

Decision log:
- SQLite database at `/tmp/anemoi.db` (or configured path)
- Decisions are durable across restarts

## Related Docs

- [[systems/prometheus/opt/stacks/ingress/traefik/traefik.md]] (reverse proxy)
- [[systems/prometheus/opt/stacks/ai/docker-compose.yml]] (AI stack)
- [Anemoi Repository](C:\Users\Alex Lucero\source\repos\anemoi\)

## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Prometheus / Anemoi Governance |
| Host/system/device owner | Prometheus (Ubuntu) |
| Runtime type | Rust binary (Cargo workspace) |
| Source of truth | `config/anemoi.live.yaml` + LlamaSwap roster |
| Config path | `/home/alex/stacks/ai/anemoi/config/anemoi.live.yaml` |
| Secret requirements | None committed; auth from environment |
| Network ports | `127.0.0.1:7070` (Anemoi daemon) → Traefik :443 |
| Dependencies | LlamaSwap runtime, Traefik proxy, Docker network |
| Backup requirement | Git-backed configuration + decision logs |
