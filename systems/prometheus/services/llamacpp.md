# llama.cpp Runtime

Last validated: 2026-05-20

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
| `/mnt/local/nvme/ai/runtimes/atomic-llama-cpp-turboquant` | Unified MTP + turbo runtime | Built 2026-05-19 from `feature/turboquant-kv-cache` branch; combines Gemma 4 MTP, Qwen 3.6 NextN, and turbo KV cache in one binary |
| `/mnt/local/nvme/ai/runtimes/llama-cpp-turboquant` | Active router runtime | Used by `llamacpp-router.service` on 2026-05-17 |
| `/mnt/local/nvme/ai/runtimes/ik_llama.cpp` | Installed llama.cpp fork | Validated source and binary support MTP; turbo cache support is not confirmed in this installed tree |
| `/mnt/local/nvme/ai/models/gguf` | Shared GGUF model store | Disposable / curated runtime cache by current docs |
| `/mnt/local/nvme/ai/profiles/llama-router-models.ini` | Active router model preset file | Root-owned live config |

## Validated Capabilities

Live binary help output validated on 2026-05-20:

| Runtime | MTP / NextN support | Turbo cache support | Notes |
|---|---|---|---:|---:|---|
| `atomic-llama-cpp-turboquant` | Yes (Gemma 4 MTP `--spec-type mtp`; Qwen 3.6 NextN `--spec-type nextn`) | Yes (turbo3/turbo2) | Unified binary built from fork; validated on Qwen 3.6 27B (+28% gen throughput) |
| `llama-cpp-turboquant` | No (`--spec-type` flags absent) | Yes | Original turboquant v9080; all non-MTP models use this binary |
| `ik_llama.cpp` | Partial (`--spec-stage mtp` present, NextN absent) | No | Retained for future MTP support; currently no models require it |

The `atomic-llama-cpp-turboquant` binary replaces the need for two separate runtimes. Models requiring speculative decoding (Qwen 3.6 NextN, Gemma 4 MTP) use this binary. All other models continue to use `llama-cpp-turboquant`.

## Active Router State

Live state after restart on 2026-05-17:

- `llamacpp-router.service` is enabled and active.
- Main process is `llama-server`.
- Router mode listens on `http://172.17.0.1:8084`.
- `/v1/models` advertises the configured router profiles.
- New model profiles use `cache-type-k = turbo3` and `cache-type-v = turbo2` (downgraded from turbo4/turbo3 on 2026-05-19 for lower VRAM overhead).

## Model Profiles

Model inventory is tracked in [[systems/prometheus/inventory]].

The router profile file currently includes GGUF profiles for:

- `gemma-4-26b-a4b-it-128k`
- `qwen3.5-122b-a10b-128k`
- `glm-4.6v-128k`
- `glm-4.7-flash-128k`
- `granite-4.1-30b-128k`
- `granite-4.1-8b-128k`

The Qwen MTP router profiles `qwen3.6-35b-a3b-128k`, `qwen3.5-9b-128k`, and `qwen3.6-27b-128k` were removed from the live router config on 2026-05-17 after load validation showed the installed runtimes do not support those unsloth MTP GGUF variants. Their replacement non-MTP GGUF profiles are tracked under [[systems/prometheus/services/llama-swap]].

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
