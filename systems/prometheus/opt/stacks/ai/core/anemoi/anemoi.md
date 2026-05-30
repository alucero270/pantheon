# anemoi

Last validated: 2026-05-28

> **Status: informal deployment.** Anemoi is running on Prometheus as a foreground `cargo run` debug build under `alex@prometheus`. No systemd unit, no container, no installed release binary. The process is parent-1 orphaned (its launching shell has exited), will not restart on reboot, and has no log rotation. Treat as `Needs validation` until formalized; see [[#Needs Validation]].

## Purpose

Anemoi is a local-first inference governance daemon. It owns request-to-domain-to-residency-group scheduling, runtime inspection, policy scoring, and structured decision telemetry over local model runtimes (llama-swap on this host). It does not execute inference itself; in v1 it returns a model-load handoff decision and (with the live-execute gate) calls the runtime's `load_model` endpoint.

Upstream architecture and product boundary are documented in the [anemoi repository](https://github.com/alucero270/anemoi) `README.md` and `AGENTS.md`. This page documents Prometheus-specific deployment evidence.

## Hosting

| Field | Value |
|---|---|
| Owning system | [[systems/prometheus]] |
| Runtime type | Foreground process (no systemd, no container) |
| Process owner | `alex` |
| Parent process | `systemd` (PID 1) — launcher shell exited; daemon was reparented |
| Process PID at probe | `1033493` |
| Binary | `/home/alex/anemoi/target/debug/anemoi-daemon` (debug build, ~92 MB) |
| Source checkout | `/home/alex/anemoi` |
| Source branch | `issue/15-improve-models-endpoint` |
| Source HEAD | `c808b5b649528dd6664ba837fdf2d8121c3b689a` |
| Source last commit | `feat(config): add prometheus llama-swap live config profile` (2026-05-28 08:48 +0200) |
| Binary build time | `2026-05-28T06:34:12Z` |
| Process start time | `2026-05-28T06:52:52Z` |
| Listen address | `0.0.0.0:7070` (env `ANEMOI_BIND=0.0.0.0:7070`) |
| Config file | `config/anemoi.prometheus.yaml` (relative to cwd `/home/alex/anemoi`; env `ANEMOI_CONFIG=config/anemoi.prometheus.yaml`) |
| Upstream runtime | `llama_swap` adapter pointed at `http://172.17.0.1:8085` (env `ANEMOI_LLAMA_SWAP_BASE_URL`) |
| Upstream auth | `${ANEMOI_LLAMA_SWAP_AUTH_TOKEN}` resolved at config-load time |
| Anemoi auth | **None** — anemoi v1 has no API auth; the daemon is fully unauthenticated to any caller that reaches `:7070` |
| Live-execute gate | `ANEMOI_ENABLE_LIVE_EXECUTE` was **not** set in the running process environment — `/execute` runs in dry-run mode; `load_model` is not called on llama-swap |

## Surface

`GET /openapi.json` reports `info.version=0.1.0` and the following paths:

- `GET /health`
- `GET /status`
- `GET /residents`
- `POST /decide`
- `POST /execute`
- `GET /decisions/{id}`
- `GET /explain/{id}`

`/staging` returned a valid JSON body on probe but is not declared in the running daemon's OpenAPI document. The Prompt 28 inference-forwarding surface (`POST /v1/chat/completions`, `GET /v1/models`) is **not** present on this build, consistent with `issue/15-improve-models-endpoint` being the branch where that work is in progress.

## Network and Exposure

| Path | Status |
|---|---|
| Direct `http://0.0.0.0:7070` on prometheus | Reachable on every LAN address bound to prometheus, **unauthenticated** |
| Direct `http://172.17.0.1:7070` on prometheus | Reachable from Docker bridge, **unauthenticated** |
| Traefik front `http://anemoi.home.arpa` | Routed via `/opt/traefik/dynamic/anemoi.yml` to `http://172.17.0.1:7070`. `anemoi-http` router currently applies `redirect-to-https@file`. The same auth-header strip pattern as llama-swap applies — see the 2026-05-28 fix in [[systems/prometheus/opt/stacks/ingress/traefik/config/README]]. The equivalent single-line swap on `anemoi.yml` is pending. |
| Traefik front `https://anemoi.home.arpa` | TLS handled by Traefik with the `home.arpa` self-signed wildcard cert. `security-headers@file` + `ollama-allowlist@file` middlewares apply. |

> **Security note:** because the daemon binds `0.0.0.0:7070` without auth, the LAN allowlist on the Traefik front is **bypassable** by anyone who can reach prometheus's primary LAN IP on port 7070 directly. The Traefik allowlist only constrains traffic to `anemoi.home.arpa`. This is a real exposure surface, not just a documentation concern.

## Configuration

Config file at `/home/alex/anemoi/config/anemoi.prometheus.yaml` declares:

- 1 domain: `coding` with rosters `[small_swarm, medium_workers, large_context]`
- 3 residency groups, 6 models total, all targeting `llama_swap`:
  - `small_swarm` (keep_hot): `qwen3.5-9b-gpu`, `granite-4.1-8b-gpu`
  - `medium_workers`: `qwen3.6-35b-a3b-mtp`, `gemma-4-26b-a4b-it-mtp`
  - `large_context`: `minimax-256k`, `qwen3.5-122b-a10b-mtp`
- 1 runtime: `llama_swap` (`base_url` and `auth_token` resolved from env)
- Continuity: `keep_small_worker_hot: true`, `max_blank_wait_ms: 2000`, `prefer_degraded_response_over_silence: true`

All `vram_required_mb`, `ram_required_mb`, and `cold_load_estimate_ms` values in the config are committed estimates. Their accuracy under live load — particularly with llama-swap's `matrix` colocation solver — has not been correlated with measured residency data documented in [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]] §"Active models".

`/status` reports `domains=1, models=6, runtimes=1, residency_groups=3`, matching the file.

## Validation Commands

Read-only smoke (run on prometheus or from an allowlisted LAN client):

```bash
curl -fsS http://127.0.0.1:7070/health
curl -fsS http://127.0.0.1:7070/status
curl -fsS http://127.0.0.1:7070/residents
curl -fsS -H 'Content-Type: application/json' \
  -d '{"domain":"coding","mode":"interactive","latency_budget_ms":1500}' \
  http://127.0.0.1:7070/decide
ps -p 1033493 -o pid,etime,command
```

Backend reachability from anemoi's perspective (llama-swap behind the `llama_swap` adapter):

```bash
curl -fsS -H 'Authorization: Bearer LOCAL' http://172.17.0.1:8085/v1/models | jq '.data | length'
```

## Backup and Recovery

Preserve sanitized copies of:

- `config/anemoi.prometheus.yaml` (Git-tracked in the anemoi repo at `c808b5b` and present in this checkout)

The debug binary at `/home/alex/anemoi/target/debug/anemoi-daemon` is reproducible from the checkout via `cargo build -p anemoi-daemon` on the same branch and is not authoritative. No host-only secrets are committed in the config; `${ANEMOI_LLAMA_SWAP_AUTH_TOKEN}` is resolved from the process environment.

There is no rollback snapshot pattern yet because there is no installed release artifact to roll back to. Restart procedure is currently "shell into prometheus, cd to the checkout, re-run `cargo run`."

## Needs Validation

- **Formalize the deployment.** Decide between (a) a systemd unit launching a release-build binary, (b) a container under the AI compose stack, or (c) keep the foreground process. Document the chosen approach as the authoritative source before treating anemoi as a running service.
- **Bind address.** Decide whether `0.0.0.0:7070` is acceptable given anemoi v1 has no auth. Options: bind to `172.17.0.1:7070` (Docker bridge only, so the Traefik allowlist is load-bearing), or add auth at the daemon, or accept the exposure as documented.
- **Traefik redirect-strip-auth fix on `anemoi.yml`.** Parallel to the 2026-05-28 fix on `llama-swap.yml` documented in [[systems/prometheus/opt/stacks/ingress/traefik/config/README]]. Pending a separate live-change iteration.
- **Drift between branches.** The running daemon is on `issue/15-improve-models-endpoint @ c808b5b`. The anemoi upstream `main` has additional commits not present on this branch. Decide whether to track `main` (which would lose the in-progress models endpoint work) or merge `main` into the branch before deploying.
- **Config estimates vs. measured load.** Reconcile `vram_required_mb` / `cold_load_estimate_ms` in `anemoi.prometheus.yaml` with the measured VRAM and timing data in [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]] §"Active models". Anemoi's policy scoring depends on these numbers.
- **`/staging` OpenAPI declaration.** Endpoint responds but is not declared in `/openapi.json`. Upstream concern; not a deployment issue.

## Related Docs

- [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]]
- [[systems/prometheus/opt/stacks/ingress/traefik/config/README]] — 2026-05-28 redirect-strip-auth fix that this service will benefit from once mirrored on `anemoi.yml`
- [[systems/prometheus/inventory]]
