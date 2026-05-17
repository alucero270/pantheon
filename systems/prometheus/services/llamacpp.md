# llama.cpp Runtime

Last validated: 2026-05-17

## Purpose

`llama.cpp` runtimes provide local GGUF inference on Prometheus outside the Ollama container workflow.

This service document covers the local llama.cpp-derived runtime trees, the active router service, model profile paths, and capability notes validated from the installed binaries.

## Hosting

| Field | Value |
|---|---|
| Owning system | [[systems/prometheus]] |
| Runtime type | Native systemd service and local compiled runtimes |
| Active service | `llamacpp-router.service` |
| Service file | `/etc/systemd/system/llamacpp-router.service` |
| Start script | `/mnt/local/nvme/ai/profiles/start-scripts/llama-router.sh` |
| Router listen address | `172.17.0.1:8084` |
| API key posture | Local API key required; do not commit secrets |

## Runtime Paths

| Path | Role | Notes |
|---|---|---|
| `/mnt/local/nvme/ai/runtimes/llama-cpp-turboquant` | Active router runtime | Used by `llamacpp-router.service` on 2026-05-17 |
| `/mnt/local/nvme/ai/runtimes/ik_llama.cpp` | Installed llama.cpp fork | Validated source and binary support MTP; turbo cache support is not confirmed in this installed tree |
| `/mnt/local/nvme/ai/models/gguf` | Shared GGUF model store | Disposable / curated runtime cache by current docs |
| `/mnt/local/nvme/ai/profiles/llama-router-models.ini` | Active router model preset file | Root-owned live config |

## Validated Capabilities

Live binary help output validated on 2026-05-17:

| Runtime | MTP support | Turbo cache support | Evidence |
|---|---:|---:|---|
| `ik_llama.cpp` | Yes | Needs validation / not proven | Help and source advertise `--multi-token-prediction`, `--spec-stage mtp`, and MTP code paths; searched source did not show `turbo2`, `turbo3`, or `turbo4` cache implementations |
| `llama-cpp-turboquant` | Needs validation for MTP | Yes | Help advertises turbo cache types; MTP-specific flag was not present in the checked help output |

Use `ik_llama.cpp` when MTP behavior is required. Use `llama-cpp-turboquant` when turbo KV cache types are required. A combined MTP plus turboquant runtime is not confirmed in the installed trees as of this validation.

## Active Router State

Live state after restart on 2026-05-17:

- `llamacpp-router.service` is enabled and active.
- Main process is `llama-server`.
- Router mode listens on `http://172.17.0.1:8084`.
- `/v1/models` advertises the configured router profiles.
- New model profiles use `cache-type-k = turbo4` and `cache-type-v = turbo3`.

## Model Profiles

Model inventory is tracked in [[systems/prometheus/inventory]].

The router profile file currently includes newly installed GGUF profiles for:

- `qwen3.6-35b-a3b-128k`
- `qwen3.5-9b-128k`
- `qwen3.6-27b-128k`
- `gemma-4-26b-a4b-it-128k`
- `qwen3.5-122b-a10b-128k`
- `glm-4.6v-128k`
- `glm-4.7-flash-128k`
- `granite-4.1-30b-128k`
- `granite-4.1-8b-128k`

## Validation Commands

```bash
systemctl status llamacpp-router.service
curl -fsS -H 'Authorization: Bearer LOCAL' http://172.17.0.1:8084/v1/models
/mnt/local/nvme/ai/runtimes/ik_llama.cpp/build/bin/llama-server --help | grep -Ei 'mtp|turbo|cache-type'
/mnt/local/nvme/ai/runtimes/llama-cpp-turboquant/build/bin/llama-server --help | grep -Ei 'mtp|turbo|cache-type'
```

## Backup and Recovery

Current docs classify local model and runtime trees as operationally important but not authoritative.

Preserve sanitized copies of:

- service unit content
- start scripts
- model profile files
- selected runtime build provenance

Do not treat GGUF model caches as authoritative unless a future decision promotes them.

## Related Docs

- [[systems/prometheus/services/ai-runtime]]
- [[systems/prometheus/services/llama-swap]]
- [[systems/prometheus/inventory]]
- [[systems/prometheus/architecture/storage-authority-map]]
- [[systems/prometheus/procedures/ai-stack-initialization]]
