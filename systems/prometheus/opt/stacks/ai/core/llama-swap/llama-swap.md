# llama-swap

Last validated: 2026-05-20

## Purpose

`llama-swap` provides an OpenAI-compatible model switching proxy for local llama.cpp-compatible backends.

On Prometheus it is installed as a native systemd service and configured to launch `llama-cpp-turboquant` backends on demand for the installed GGUF models.

## Hosting

| Field | Value |
|---|---|
| Owning system | [[systems/prometheus]] |
| Runtime type | Native systemd service |
| Service name | `llama-swap.service` |
| Service file | `/etc/systemd/system/llama-swap.service` |
| Binary | `/mnt/local/nvme/ai/runtimes/llama-swap/llama-swap` |
| Version validated | `214` |
| Config file | `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml` |
| Listen address | `172.17.0.1:8085` |
| Backend runtime | `/mnt/local/nvme/ai/runtimes/llama-cpp-turboquant/build/bin/llama-server` (v9080) — non-MTP models |
| NextN / MTP runtime | `/mnt/local/nvme/ai/runtimes/atomic-llama-cpp-turboquant/build/bin/llama-server` (built 2026-05-19) — `qwen3.6-*-mtp` and Gemma 4 MTP models |
| Backend port range | `19080+` (19080 avoids Traefik dashboard on `127.0.0.1:18080`) |
| API key | `LOCAL`; use `Authorization: Bearer LOCAL`. As of 2026-05-28 this works on both `http://172.17.0.1:8085` and `http://llama-swap.home.arpa` (Traefik LAN front). Before the 2026-05-28 Traefik fix in [[systems/prometheus/opt/stacks/ingress/traefik/config/README]], HTTP clients hitting `llama-swap.home.arpa` got `401` because the HTTP→HTTPS redirect stripped `Authorization`; `X-API-Key: LOCAL` was the working workaround on that path. |

## Installation State

Live install validated on 2026-05-17:

- Upstream Linux amd64 release archive checksum verified before install.
- Binary installed under `/mnt/local/nvme/ai/runtimes/llama-swap`.
- `llama-swap.service` is enabled and active.
- Health endpoint returns `OK`.
- `/v1/models` lists one exposed model ID per configured profile; aliases are not included in the model list.

## Model Configuration

The live config launches `llama-cpp-turboquant` with turbo KV cache settings:

- `--cache-type-k turbo3`
- `--cache-type-v turbo2`

These cache types are provided by the installed `llama-cpp-turboquant` runtime. They are not confirmed in the installed `ik_llama.cpp` tree. The switch from turbo4/turbo3 to turbo3/turbo2 was made on 2026-05-19 after benchmarking showed no quality regression and lower VRAM overhead across all models.

### Active models (validated 2026-05-20)

Optimized parameters determined via batch-size/ubatch-size sweeps. GPU-primary models use most VRAM and are swapped one at a time. CPU-agent models stay loaded alongside GPU models via the `matrix` solver.

Key constraints: RTX 4000 Ada 20 GB VRAM, 94 GB system RAM, 56 threads dual-socket CPU.

#### GPU-primary models (one active at a time, swapped via matrix solver)

| Model ID | Batch | Ubatch | Prompt (t/s) | Gen (t/s) | VRAM (MiB) | Notes |
|---|---|---|---|---|---|---|---|
| `gemma-4-26b-a4b-it` | 256 | 32 | 32 | 70 | ~8,000 | MoE 4B active; thinking model; 128K ctx |
| `gemma-4-31b-it` | 256 | 32 | ~2,000 (warm) | 17.5 | 18,032 | Dense 31B; 128K ctx |
| `qwen3.5-122b-a10b` | 64 | 16 | 26 | 11.7 | 19,684 | MoE 10B active; `n-cpu-moe=37`; 128K ctx |
| `glm-4.6v` | 64 | 16 | 16 | 8.6 | ~15,000 | MoE ~200B; `n-cpu-moe=38`; 128K ctx |
| `glm-4.7-flash` | 128 | 32 | 83 | 85.6 | ~8,000 | MoE thinking model; 128K ctx |
| `granite-4.1-30b` | 128 | 32 | 81 | 19.6 | ~16,000 | MoE 30B; 80K ctx (compact to fit VRAM) |
| `nemotron-udq2-128k` | 64 | 16 | 19 | 12.8 | ~19,000 | MoE 120B; `n-cpu-moe=64`; 128K ctx; flash-attn on |
| `nemotron-udq3-128k` | 64 | 16 | 11 | 10.5 | ~19,000 | MoE 120B; `n-cpu-moe=71`; 128K ctx; flash-attn on |
| `minimax-80k` | 64 | 16 | 5 | 6.2 | ~19,000 | MoE 230B; `n-cpu-moe=55`; 80K ctx; flash-attn on |
| `minimax-96k` | 64 | 16 | 4 | 6.5 | ~19,000 | MoE 230B; `n-cpu-moe=56`; 96K ctx; flash-attn on |
| `minimax-128k` | 64 | 16 | 3 | 7.0 | ~19,000 | MoE 230B; `n-cpu-moe=57`; 128K ctx; flash-attn on |
| `qwen3.6-35b-a3b` | 256 | 32 | 46 | 80 | ~6,000 | MoE 3B active; 64K ctx; non-MTP |
| `qwen3.6-35b-a3b-mtp` | 256 | 32 | TBD | TBD | ~8,000 | MoE 3B active; 64K ctx; NextN; download in progress |
| `qwen3.6-27b` | 256 | 32 | 255 | 19.8 | 14,342 | Dense 27B; 64K ctx; non-MTP |
| `qwen3.6-27b-mtp` | 64 | 16 | 136 | 25.6 | 16,588 | Dense 27B; 64K ctx; NextN; +28% gen over non-MTP |

#### CPU-agent models (always available alongside any GPU model)

| Model ID | Batch | Ubatch | Parallel | Prompt (t/s) | Gen (t/s) | Notes |
|---|---|---|---|---|---|---|
| `granite-4.1-8b` | 256 | 32 | 5 | 38 | 4.8 | Dense 8B; `n-gpu-layers=0`; 128K ctx |
| `qwen3.5-9b` | 256 | 32 | 5 | 30 | 4.9 | Dense 9B; `n-gpu-layers=0`; 128K ctx |

CPU-agent models run entirely on CPU (`n-gpu-layers=0`). Their gen speed is bottlenecked by system memory bandwidth regardless of thread count. They use `--parallel 5` to handle concurrent requests from agent swarms.

Dense models that can fit all weights in GPU should prefer full GPU residency with reduced context over CPU/GPU layer splitting.

The Granite 30B 128K split profile was replaced by an 80K full-GPU profile because the 128K full-GPU projection exceeded available VRAM. The 80K profile loads all 65 layers on GPU and keeps turbo KV on GPU.

OpenWebUI duplicate model rows were removed from the live `llama-swap` listing on 2026-05-17 by disabling alias inclusion and exposing the short profile IDs above. MiniMax and Nemotron profiles were copied from the existing `llamacpp-router.service` preset file on 2026-05-17 as known-good starting profiles. Qwen non-MTP GGUF profiles were added to replace the unsupported MTP variants.

### NextN Speculative Decoding

The `atomic-llama-cpp-turboquant` binary (built 2026-05-19) supports Qwen 3.6 NextN speculative decoding. NextN uses the combined `*_MTP.gguf` with `--spec-type nextn --model-draft <same-file>`. Gemma 4 MTP head support was removed — the `gemma-4-31b-it-mtp` entry no longer uses an MTP head and runs as a non-MTP IQ3_XXS model.

Qwen 3.6 27B MTP benchmark (2026-05-20):

| Metric | Non-MTP | MTP NextN | Δ |
|---|---|---|---|
| Cold prompt | 69 t/s | 136 t/s | +97% |
| Cold gen | 19.4 t/s | 25.6 t/s | +32% |
| Warm gen | 19.8 t/s | 25.3 t/s | +28% |
| VRAM | 14,342 MiB | 16,588 MiB | +2,246 MiB |

MTP models use the AtomicChat upstream `*_MTP.gguf` (built with unsloth MTP-aware imatrix), not the unsloth SSM-based MTP variants that failed to load on 2026-05-17.

### Disabled models (SSM-based unsloth MTP)

The following unsloth MTP GGUF variants included SSM architecture tensors (`ssm_conv1d`) not supported by any current llama.cpp binary, and the unsupported local directories were removed on 2026-05-17 after non-MTP replacements were installed:

| Model ID | Removed GGUF directory |
|---|---|
| `qwen3.6-35b-a3b-128k` | `qwen3.6-35b-a3b-mtp-unsloth-ud-iq4-xs` |
| `qwen3.5-9b-128k` | `qwen3.5-9b-mtp-unsloth-ud-q4-k-xl` |

The `qwen3.6-27b-128k` entry has been superseded by the working `qwen3.6-27b-mtp` using the AtomicChat combined GGUF.

Standard non-MTP variants are configured under the short model IDs in the active model table.

### Matrix Co-Location

llama-swap's `matrix` DSL solver manages concurrent model loading. The matrix defines valid sets of simultaneously-loaded models; the solver picks the set that minimizes evictions when a new model is requested.

Current matrix (2026-05-20):

```yaml
matrix:
  vars:
    g26: gemma-4-26b-a4b-it
    g31: gemma-4-31b-it
    q122: qwen3.5-122b-a10b
    g4v: glm-4.6v
    gf4: glm-4.7-flash
    gr30: granite-4.1-30b
    n2: nemotron-udq2-128k
    n3: nemotron-udq3-128k
    mx8: minimax-80k
    mx9: minimax-96k
    mx12: minimax-128k
    q35: qwen3.6-35b-a3b
    q35m: qwen3.6-35b-a3b-mtp
    q27: qwen3.6-27b
    q27m: qwen3.6-27b-mtp
    g8: granite-4.1-8b
    q9: qwen3.5-9b
  evict_costs:
    q122: 50   # 122B slow cold start
    g4v: 50    # 200B+ slow cold start
    mx8..mx12: 60  # 230B slowest
    n2..n3: 40     # 120B slow
    q27: 10    # moderate
    q27m: 10   # moderate (same model, MTP overhead)
    g31: 10
    q35: 5     # fast
    q35m: 5    # fast
    g26: 5
    gf4: 5
    gr30: 5
    g8: 1      # fastest (CPU, instant load)
    q9: 1
  sets:
    colocated: "(g26 | g31 | q122 | g4v | gf4 | gr30 | n2 | n3 | mx8 | mx9 | mx12 | q35 | q35m | q27 | q27m) & (g8 & q9)"
```

The set `(GPU-primary) & (CPU-agents)` means:

The set `(GPU-primary) & (CPU-agents)` means:

- Any single GPU model can run alongside all CPU-agent models.
- Switching GPU models evicts the previous GPU model but **keeps CPU models loaded**.
- CPU agents stay warm across GPU swaps (1-2s TTFT vs 12s+ cold load).
- Requesting a CPU agent while a GPU model is active does not evict the GPU model.

#### Solver behavior

1. Request arrives for model X.
2. If X is already running, forward immediately.
3. Find the valid set containing X with the fewest evictions (weighted by `evict_costs`).
4. Evict what must stop, start what must start, forward request.

Models not in any set (should not occur in current config) fall back to default solo behavior.

### Agent Swarm on CPU

Small CPU models (`granite-4.1-8b`, `qwen3.5-9b` with `--n-gpu-layers 0`) can serve multiple concurrent agent requests via `--parallel 5`. Performance under concurrent load:

| Scenario | Success | Avg gen (t/s) | Throughput |
|---|---|---|---|
| Single granite-8b | 1/1 | 4.8 | 0.3 req/s |
| 5 concurrent granite-8b | 5/5 | 2.3 | 0.1 req/s |
| 10 concurrent granite-8b | 10/10 | 4.3 | 0.6 req/s |
| Mixed granite-8b + qwen-9b | degrades severely | 0.3 | 0.0 req/s |

**Recommendation**: Use a single CPU model type for swarms. Granite-8b handles 5-10 concurrent agents with gen speed dropping from ~5 to ~2-3 t/s. Avoid mixing different CPU models simultaneously.

### Benchmark Notes (2026-05-19)

All benchmarks performed with llama-cpp-turboquant v9080, turbo3/turbo2 KV cache, mmap enabled. Prompt=512 tok, gen=128 tok unless noted.

**General findings:**

- **mmap** is always faster than no-mmap (3×+ improvement on large MoE models).
- **direct_io** regresses performance for all models (disables OS page cache).
- **Batch-size/ubatch-size** sweet spot: 64-256 / 16-32. Larger values for small dense models, conservative for large MoE.
- **CPU-only** inference is bottlenecked by memory bandwidth (~4 t/s gen regardless of thread count).
- **mlock** caused crashes; not recommended for large models.

## Network and Exposure

`llama-swap` is bound to Docker bridge host address `172.17.0.1:8085`.

Traefik also routes `llama-swap.home.arpa` to this backend for approved local-network clients.

OpenWebUI was pointed to this endpoint on 2026-05-17 through `OPENAI_API_BASE_URLS=http://host.docker.internal:8085/v1`.

## Validation Commands

```bash
systemctl status llama-swap.service
curl -fsS http://172.17.0.1:8085/health
curl -fsS -H 'Authorization: Bearer LOCAL' http://172.17.0.1:8085/v1/models
journalctl -u llama-swap.service -n 100 --no-pager
```

## Backup and Recovery

Preserve sanitized copies of:

- `/etc/systemd/system/llama-swap.service`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml`

The binary is reinstallable from upstream release artifacts and is not authoritative.

## Related Docs

- [[systems/prometheus/opt/stacks/ai/core/llamacpp/llamacpp]]
- [[systems/prometheus/opt/stacks/ai/core/ai-runtime/ai-runtime]]
- [[systems/prometheus/inventory]]
- [[systems/prometheus/architecture/storage-authority-map]]
