# ADR-011: llama-cpp-turboquant as the llama-swap Backend

## Status

Accepted

## Context

Prometheus runs two native llama.cpp-compatible server binaries:

| Binary | Fork | Version |
|---|---|---|
| `ik_llama.cpp` | ikawrakow/ik_llama.cpp | v4505 (1f8c603d) |
| `llama-cpp-turboquant` | TheTom/llama-cpp-turboquant | v9080 (e69af784a) |

These are independent forks of upstream llama.cpp with different feature sets. They are not interchangeable.

`llama-swap` is a model-switching proxy that launches a llama.cpp-compatible server process on demand for each model. Its config specifies which binary to use.

The original llama-swap config was written with `--cache-type-k turbo4 --cache-type-v turbo3` in the common args but pointed at the `ik_llama.cpp` binary. This configuration was always broken: turbo2/turbo3/turbo4 are proprietary KV cache quantization types invented by TheTom and only exist in `llama-cpp-turboquant`. ik_llama.cpp does not have them and rejects the flags at startup.

During model validation on 2026-05-17, additional issues were found:

**ik_llama.cpp (v4505) — Granite 4.1 architecture bug**
- Models: `granite-4.1-8b-UD-Q3_K_XL`, `granite-4.1-30b-UD-Q3_K_XL`
- Symptom: generates only spaces or repetitive garbage tokens regardless of KV cache type or context size
- Root cause: likely incorrect handling of Granite 4.1's architecture-specific scaling parameters (`embedding_scale=12`, `logit_scale=16`, `residual_scale=0.22`, `attention_scale=0.007812`)
- The same GGUF files produce correct output with `llama-cpp-turboquant`
- Tracked in: [issue #108](https://github.com/alucero270/pantheon/issues/108)

**MTP GGUF incompatibility — both binaries**
- Models: `qwen3.6-35b-a3b-mtp`, `qwen3.5-9b-mtp`, `qwen3.6-27b-mtp` (unsloth variants)
- Symptom: `missing tensor 'blk.32.ssm_conv1d.weight'` at load time
- Root cause: unsloth MTP-variant GGUFs include SSM architecture tensors not implemented in either binary
- Tracked in: [issue #107](https://github.com/alucero270/pantheon/issues/107)

**Port conflict**
- llama-swap `startPort: 18080` conflicts with Traefik's dashboard container port mapping (`127.0.0.1:18080->8080/tcp`)
- Resolution: `startPort` changed to `19080`

---

## Decision

Use `llama-cpp-turboquant` as the llama-swap backend binary.

Retain `ik_llama.cpp` on disk — it is the fork most actively developing MTP support and is the most likely candidate to support unsloth MTP GGUFs once SSM tensor support lands.

Disable the three MTP Qwen model slots in llama-swap config until non-MTP GGUFs are downloaded.

---

## Rationale

- `llama-cpp-turboquant` is the only binary that correctly serves all currently loadable models (Granite 4.1, GLM 4.x, Gemma 4)
- turbo4/turbo3 KV cache types are turboquant-exclusive and provide better precision-per-byte than q8_0 without the degenerate sampling behavior observed with ik_llama.cpp
- ik_llama.cpp has no models it can serve that turboquant cannot serve better, as of v4505

---

## Consequences

### Positive

- All non-MTP models load and generate correctly via llama-swap
- turbo4/turbo3 KV cache types work as originally intended in the config
- Port conflict with Traefik eliminated

### Negative / Tradeoffs

- turbo4/turbo3 cache types are not portable — if the backend binary ever changes back to ik_llama.cpp or upstream llama.cpp, the cache type args must be updated
- MTP Qwen slots remain disabled until non-MTP GGUFs are downloaded
- ik_llama.cpp binary is retained but currently serves no function; it will need rebuilding when MTP GGUF support arrives (source is already checked out at `/mnt/local/nvme/ai/runtimes/ik_llama.cpp/`)

---

## Conditions for Revisiting

- ik_llama.cpp adds SSM tensor support enabling unsloth MTP GGUF loading → migrate MTP model slots to ik_llama.cpp backend (llama-swap supports per-model binary overrides via the `cmd` field)
- ik_llama.cpp fixes the Granite 4.1 architecture bug → non-MTP granite models could optionally use ik_llama.cpp if turbo cache types are also added there
- TheTom's turboquant adds MTP GGUF support → MTP models can stay on turboquant, no binary split needed

---

## Implementation Notes

- Config: `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml`
- Backend macro: `tq_server: /mnt/local/nvme/ai/runtimes/llama-cpp-turboquant/build/bin/llama-server`
- Port range: `startPort: 19080` (avoids `127.0.0.1:18080` held by Traefik container)
- KV cache: `--cache-type-k turbo4 --cache-type-v turbo3` in `common_args`
- llama-swap listens on `172.17.0.1:8085`
