# llama-swap Config

## Purpose

This folder tracks sanitized llama-swap config notes and restore guidance.

## Live Config Candidates

| Live path | Purpose | Git posture |
|---|---|---|
| `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml` | llama-swap model switching config | Sanitized Git candidate after secret review |
| `/etc/systemd/system/llama-swap.service` | Native service unit | Sanitized Git candidate |

## Status

No Git-backed sanitized llama-swap config has been committed here yet.

## Live Change Notes

### 2026-05-26 MiniMax TurboQuant KV cache tuning

Live path: `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml`

Rollback snapshots created on Prometheus:

- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.bak-20260526T182803Z`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.bak-20260526T182902Z`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.bak-20260526T183050Z`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.bak-20260526T183130Z`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.bak-ubatch2048-20260526T201041Z`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.bak-batch4096-ubatch2048-20260526T201233Z`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.bak-batch8192-ubatch1024-20260526T201324Z`

Change:

- Tested `--cache-type-k turbo5` with `--cache-type-v turbo4`; the active TurboQuant runtime rejected `turbo5` as unsupported. Allowed turbo values stop at `turbo4`.
- Set MiniMax model-local KV cache overrides to `--cache-type-k turbo4` and `--cache-type-v turbo4`.
- Added `/usr/bin/env TURBO_AUTO_ASYMMETRIC=0` before the MiniMax `llama-server` command so TurboQuant does not auto-upgrade MiniMax K cache from `turbo4` to `q8_0`.
- Increased MiniMax `--cache-ram` from `16384` to `32768`.
- Preserved `--temp 0.7`, `--top-p 0.95`, `--top-k 40`, `--ctx-size 196608`, `--batch-size 8192`, `--n-cpu-moe 60`, and `--reasoning-budget 256`.
- Tested larger MiniMax prompt-processing microbatches after the Pi Canonis run stopped; `--ubatch-size 2048` OOMed with both `--batch-size 8192` and `--batch-size 4096`, so the live setting was changed to `--batch-size 8192` and `--ubatch-size 1024`.

Validation result:

- `turbo4/turbo4` without `TURBO_AUTO_ASYMMETRIC=0` OOMed because the runtime auto-upgraded K to `q8_0`, producing a `CUDA0 KV buffer size` of about `18972 MiB` before total model residency.
- `turbo4/turbo4` with `TURBO_AUTO_ASYMMETRIC=0` loaded successfully.
- Live MiniMax residency after the change was about `19070 MiB / 20475 MiB` VRAM.
- The backend reported `K (turbo4): 6324.00 MiB, V (turbo4): 6324.00 MiB`, prompt cache limit `32768 MiB`, and HTTP 200 on cold and warm OpenAI-compatible probes.
- Warm probe showed prompt-cache reuse with `cached_tokens=31` and completed HTTP 200.
- `--ubatch-size 2048` failed during startup compute-buffer allocation: `n_ubatch = 2048`, CUDA compute allocation about `2376 MiB`, followed by `cudaMalloc failed: out of memory` and HTTP 502 from llama-swap.
- `--batch-size 4096 --ubatch-size 2048` failed the same way, confirming the `2048` microbatch allocation was the limiting factor rather than logical batch size.
- `--batch-size 8192 --ubatch-size 1024` loaded successfully, passed health check, and returned HTTP 200 on cold and warm OpenAI-compatible probes. Live residency was about `19224 MiB / 20475 MiB` VRAM. The warm probe reported `cached_tokens=31`, prompt eval about `15.9 tok/s` on the tiny cached request, and generation about `9.65 tok/s`.

Needs validation:

- Run a real OpenCode/Pi coding-agent task to check whether `turbo4/turbo4` improves long-context instruction retention and scope control versus the prior inherited `turbo3/turbo2`.
- Decide whether to apply `--cache-ram` to additional models. For co-located models, use smaller per-model limits first because `32768 MiB` per resident model can overcommit system RAM if multiple prompt caches grow at once.

### 2026-05-26 MiniMax quality-focused retry profile

Live path: `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml`

Rollback snapshot created on Prometheus:

- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260526T064738Z.minimax-rb256-temp07.bak`

Tested change:

- Model ID: `minimax-256k`
- Changed `--reasoning-budget 125` to `--reasoning-budget 256`.
- Changed `--temp 1.0` to `--temp 0.7`.
- Preserved `--top-p 0.95`, `--top-k 40`, `--n-cpu-moe 60`, `--ctx-size 196608`, `--batch-size 8192`, `--ubatch-size 512`, prompt cache, and checkpoint settings.

Validation result:

- `llama-swap.service` reloaded the watched config.
- MiniMax launched successfully and passed health check on `http://localhost:19090/health`.
- Direct OpenAI-compatible probe returned HTTP 200.
- Probe showed `reasoning-budget=256`, about `14846 MiB` VRAM used, about `6.5 tok/s` prompt evaluation on the tiny cold probe, and about `9.3 tok/s` generation.
- OpenCode remains configured for `llama-swap/minimax-256k` for both `model` and `small_model`, with provider timeout disabled and `chunkTimeout = 21600000`.

Needs validation:

- Run the Canonis MCP issue workload for issues `#3`, `#4`, `#5`, and `#7` and compare coherence against the prior MiniMax `--reasoning-budget 125`, `--temp 1.0` run.
- Watch for renewed long-request `context canceled` events during cold or replay-heavy OpenCode prompts.

Tracking issue: [#117](https://github.com/alucero270/pantheon/issues/117)

### 2026-05-25 OpenCode local-provider timeout fix

Client-side config touched on the Windows workstation:

- `C:\Users\Alex Lucero\.config\opencode\opencode.json`

Rollback snapshot created on the Windows workstation:

- `C:\Users\Alex Lucero\.config\opencode\opencode.json.20260525T171018.nemotron-timeout.bak`

Changes:

- Moved the llama-swap provider `timeout` setting under `provider.llama-swap.options`, which is where OpenCode documents provider timeout options.
- Set `provider.llama-swap.options.timeout` to `false` to disable OpenCode's default request timeout for local long-running model calls.
- Set `provider.llama-swap.options.chunkTimeout` to `21600000` ms so long prompt-processing phases without streamed chunks do not abort local requests.
- Set both `model` and `small_model` to `llama-swap/nemotron-udiq4-256k` so OpenCode helper traffic does not reload qwen122 during a Nemotron test.

Validation result:

- The OpenCode JSON config parsed successfully after the change.
- After the change, Nemotron remained resident as `nemotron-udiq4-256k` with about `15.3 GiB` VRAM used.
- A post-change OpenCode request processed about `37,570` prompt tokens and returned HTTP 200 in about `2m14s` with no `context canceled` failure.

Needs validation:

- Run a fresh OpenCode session with a cold or replay-heavy request that lasts longer than five minutes and confirm the previous 502 `context canceled` boundary is gone.

Tracking issue: [#117](https://github.com/alucero270/pantheon/issues/117)

### 2026-05-25 MiniMax UD-IQ3_XXS cleanup

Live path: `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml`

Rollback snapshots created on Prometheus:

- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260525T083317Z.model-cleanup.bak`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260525T084519Z.qwen-nemotron-cleanup.bak`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260525T074458Z.minimax-fit-196k-cpumoe.bak`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260525T081019Z.final-moe-vram-buckets.bak`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260525T155817Z.minimax-default-sampling-rb125-cpumoe55.bak`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260525T160119Z.minimax-restore-cpumoe60-keep-sampling.bak`

Client-side rollback snapshot created on the Windows workstation:

- `C:\Users\Alex Lucero\.config\opencode\opencode.json.20260525T175847.minimax-retry.bak`

Target model path:

- `/mnt/local/nvme/ai/models/gguf/minimax-m2-7-unsloth-ud-iq3-xxs/UD-IQ3_XXS/MiniMax-M2.7-UD-IQ3_XXS-00001-of-00003.gguf`

Changes:

- Removed the old MiniMax `UD-IQ4_XS` model directory from `/mnt/local/nvme/ai/models/gguf`.
- Replaced the separate `minimax-80k`, `minimax-96k`, and `minimax-128k` llama-swap entries with one `minimax-256k` entry.
- Started MiniMax from the current qwen122 operating floor, then adjusted from load evidence.
- Set MiniMax to its GGUF-declared maximum context, `--ctx-size 196608`, because the model metadata reports `minimax-m2.context_length = 196608`.
- Tuned MiniMax to `--n-cpu-moe 60`; `--n-cpu-moe 50` OOMed, while `60` was the highest-VRAM working bucket found.
- Preserved the qwen122 cache settings: `--ubatch-size 512`, `--cache-ram 16384`, `--ctx-checkpoints 64`, and `--checkpoint-every-n-tokens 4096`.
- Increased MiniMax to `--batch-size 8192` after prompt processing tests, then increased `--reasoning-budget` from `64` to `512` for agent-style analysis.
- Retuned MiniMax to `--reasoning-budget 125` and added the MiniMax-recommended sampler defaults: `--temp 1.0`, `--top-p 0.95`, and `--top-k 40`.
- Tested moving five more MoE experts onto GPU by changing `--n-cpu-moe 60` to `55`; the load OOMed, so MiniMax was restored to the known-good `--n-cpu-moe 60`.
- Updated the llama-swap matrix aliases and eviction cost to use `mx256`.
- Started a direct streamed download of `unsloth/MiniMax-M2.7-GGUF` `UD-IQ3_XXS` shards into the model home instead of a separate Hugging Face cache directory.
- Pointed OpenCode `model` and `small_model` back to `llama-swap/minimax-256k` for the MiniMax retry while preserving the local no-timeout provider settings.

Validation result:

- All three `UD-IQ3_XXS` shards are present as real files under `/mnt/local/nvme/ai/models/gguf/minimax-m2-7-unsloth-ud-iq3-xxs/UD-IQ3_XXS`.
- `llama-swap.service` restarted successfully and `/v1/models` exposes `minimax-256k`.
- First Qwen-baseline load at `--ctx-size 262144` and `--n-cpu-moe 40` failed: projected about `41.2 GiB` device memory and failed allocating about `28.7 GiB` CUDA model buffer.
- Retest at `--ctx-size 196608` and `--n-cpu-moe 60` succeeded.
- MiniMax probe returned HTTP 200, used about `14846 MiB` VRAM, and reported about `7.6 tok/s` prompt evaluation on the small probe.
- The short `max_tokens=8` probe spent its output budget in `reasoning_content`; final-answer behavior needs a longer cap or stronger reasoning suppression test.
- Local Pi and OpenCode model lists were updated to expose `minimax-256k` as `MiniMax M2.7 UD-IQ3_XXS 196K`.
- A Pi agent run against `anemoi-rust-rewrite` reached MiniMax successfully through llama-swap, but updating the watched config file caused llama-swap to reload MiniMax and the active Pi stream ended with `Stream ended without finish_reason`.
- After the watcher-applied reload, MiniMax came back healthy with `--reasoning-budget 512`; rollback snapshot is `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260525T093351Z.minimax-reasoning512.bak`.
- Later Pi runs showed backend-healthy client cancellations rather than model crashes: llama-swap returned 502 with `context canceled` after about five minutes, while the upstream MiniMax llama-server completed the same requests with HTTP 200 immediately afterward.
- Additional long MiniMax streams logged client disconnect recovery and invalid partial stream JSON after the client disconnected. Local Pi settings were updated to disable Pi's HTTP idle timeout and set the local provider request timeout to `900000` ms.
- The `--n-cpu-moe 55` load attempt failed after model tensors loaded: CUDA allocation of about `1035 MiB` for compute buffers failed and the MiniMax process exited during startup.
- Restored `--n-cpu-moe 60` while keeping `--reasoning-budget 125` and the MiniMax sampler defaults. Direct OpenAI-compatible probe returned HTTP 200, used about `14846 MiB` VRAM, activated `reasoning-budget=125`, and reported about `6.3 tok/s` prompt evaluation and `9.4 tok/s` generation on the small probe.

Needs validation:

- Re-run the MiniMax Pi/OpenCode agent-style prompt after the `--reasoning-budget 512` change and compare final-answer quality, time-to-response, and stream stability.
- Re-run a MiniMax Pi request that lasts longer than five minutes and confirm there is no 502 `context canceled` failure at the old timeout boundary.

Tracking issue: [#117](https://github.com/alucero270/pantheon/issues/117)

### 2026-05-25 Qwen duplicate cleanup and Nemotron UD-IQ4_XS replacement

Live path: `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml`

Rollback snapshots created on Prometheus:

- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260525T084519Z.qwen-nemotron-cleanup.bak`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260525T065907Z.global-context-batch-standard.bak`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260525T074727Z.nemotron-fit-cpumoe384.bak`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260525T081019Z.final-moe-vram-buckets.bak`

Target Nemotron model path:

- `/mnt/local/nvme/ai/models/gguf/nemotron-3-super-120b-a12b-unsloth-ud-iq4-xs/UD-IQ4_XS/NVIDIA-Nemotron-3-Super-120B-A12B-UD-IQ4_XS-00001-of-00003.gguf`

Changes:

- Removed Qwen non-MTP entries that had MTP counterparts: `qwen3.6-27b` and `qwen3.6-35b-a3b`.
- Removed the matching Qwen non-MTP model directories from `/mnt/local/nvme/ai/models/gguf`.
- Preserved Qwen entries without a same-model MTP counterpart, such as `qwen3.5-9b`.
- Removed the previous Nemotron Q2/Q3 llama-swap entries and the co-located Q2 entry.
- Removed the previous Nemotron Q2/Q3 model directories from `/mnt/local/nvme/ai/models/gguf`.
- Added one replacement profile: `nemotron-udiq4-256k`.
- Started Nemotron from the current qwen122 operating floor, then adjusted from load evidence.
- Tuned Nemotron to `--n-cpu-moe 80`; `--n-cpu-moe 70` OOMed, while `80` was the highest-VRAM working bucket found.
- Preserved the qwen122 context/batch/cache settings: `--ctx-size 262144`, `--batch-size 4096`, `--ubatch-size 512`, `--reasoning-budget 64`, `--cache-ram 16384`, `--ctx-checkpoints 64`, and `--checkpoint-every-n-tokens 4096`.
- Updated the llama-swap matrix aliases and eviction cost to use `n4`.
- Started a direct streamed download of `unsloth/NVIDIA-Nemotron-3-Super-120B-A12B-GGUF` `UD-IQ4_XS` shards into the model home instead of a separate Hugging Face cache directory.
- Standardized the llama-swap model entries to the qwen122 batch floor: `--batch-size 4096` and `--ubatch-size 512`.
- Standardized context to `--ctx-size 262144` except where dense full-GPU residency required a lower context.
- Set Gemma 31B dense and MTP profiles to full-GPU residency with `--n-gpu-layers 999` and `--ctx-size 131072`.
- Set Granite 30B to full-GPU residency with `--n-gpu-layers 999` and `--ctx-size 65536`.

Validation result:

- All three Nemotron `UD-IQ4_XS` shards are present as real files under `/mnt/local/nvme/ai/models/gguf/nemotron-3-super-120b-a12b-unsloth-ud-iq4-xs/UD-IQ4_XS`.
- `llama-swap.service` restarted successfully and `/v1/models` exposes `nemotron-udiq4-256k` and no longer exposes the removed Qwen/Nemotron IDs.
- First Qwen-baseline load at `--n-cpu-moe 40` failed: projected about `39.0 GiB` device memory and failed allocating about `36.9 GiB` CUDA model buffer.
- Retest at `--n-cpu-moe 80` succeeded.
- Nemotron probe returned HTTP 200, used about `15210 MiB` VRAM, and reported about `17.8 tok/s` prompt evaluation on the small probe.
- The short `max_tokens=8` probe spent its output budget in `reasoning_content`; final-answer behavior needs a longer cap or stronger reasoning suppression test.
- Local Pi and OpenCode model lists were updated to expose `nemotron-udiq4-256k`.

Needs validation:

- Validate Nemotron with a real agent-style prompt and a completion cap large enough to observe final content.
- Validate that smaller and co-located profiles still load after the global context and batch standardization.
- Revisit Granite 30B context only if a lower batch size is acceptable; at `--batch-size 4096`, 128K did not fit with full GPU residency.

Tracking issue: [#117](https://github.com/alucero270/pantheon/issues/117)

### 2026-05-23 qwen122 non-MTP `--n-cpu-moe 35` load test

Live path: `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml`

Rollback snapshot created on Prometheus:

- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260523T224149Z.qwen122-cpu-moe35.bak`

Tested change:

- Model ID: `qwen3.5-122b-a10b`
- Changed `--n-cpu-moe 63` to `--n-cpu-moe 35`

Validation result:

- `llama-swap.service` restarted successfully and launched `qwen3.5-122b-a10b` with `--n-cpu-moe 35`.
- Load failed before a completion was returned. llama.cpp projected `20471 MiB` device memory use against about `19700 MiB` free, then failed a `149.06 MiB` CUDA allocation for the rs cache.
- llama-swap returned HTTP 502 with `unable to start process: upstream command exited prematurely but successfully`.
- The live config was restored from the rollback snapshot, returning `qwen3.5-122b-a10b` to `--n-cpu-moe 63`.
- Post-rollback validation: `llama-swap.service` active, `/v1/models` responding, GPU idle at about `4 MiB`.

Needs validation:

- Determine whether `qwen3.5-122b-a10b` can run with lower `--n-cpu-moe` only if paired with lower context, lower batch/ubatch, fewer GPU layers, or a larger GPU free-memory margin.

Tracking issue: [#117](https://github.com/alucero270/pantheon/issues/117)

### 2026-05-23 qwen122 non-MTP `--n-cpu-moe 40` load test

Live path: `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml`

Rollback snapshot created on Prometheus:

- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260523T224603Z.qwen122-cpu-moe40.bak`

Tested change:

- Model ID: `qwen3.5-122b-a10b`
- Changed `--n-cpu-moe 63` to `--n-cpu-moe 40`

Validation result:

- `llama-swap.service` restarted successfully and launched `qwen3.5-122b-a10b` with `--n-cpu-moe 40`.
- Load succeeded. The backend remained running as PID `1963172`.
- Observed GPU memory settled at about `15462 MiB` of `20475 MiB`.
- A small OpenAI-compatible chat completion returned HTTP 200 with timings around `21.2 tok/s` prompt evaluation and `12.0 tok/s` generation.
- Small completion caps returned reasoning-only content before final `content`, so final-answer behavior still needs validation with an agent-style request or an explicit reasoning suppression setting.

Needs validation:

- Determine whether the non-MTP `qwen3.5-122b-a10b` profile should include a reasoning suppression option, if supported by the active `llama-cpp-turboquant` runtime.
- Validate an agent-style coding prompt against the `--n-cpu-moe 40` profile before treating it as the preferred local-agent profile.

Tracking issue: [#117](https://github.com/alucero270/pantheon/issues/117)

### 2026-05-23 qwen122 MTP `--n-cpu-moe 40` and 256K context test

Live path: `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml`

Rollback snapshots created on Prometheus:

- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260523T225942Z.qwen122-mtp-cpu-moe40.bak`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260523T230032Z.qwen122-mtp-ctx262144.bak`

Tested changes:

- Model ID: `qwen3.5-122b-a10b-mtp`
- Changed `--n-cpu-moe 63` to `--n-cpu-moe 40`
- Changed `--ctx-size 131072` to `--ctx-size 262144`

Validation result:

- `--n-cpu-moe 40` at 128K context loaded successfully and returned final `content=OK`.
- Observed 128K VRAM settled at about `14048 MiB` of `20475 MiB`.
- 128K probe timings were about `24.0 tok/s` prompt evaluation and `13.8 tok/s` generation.
- The 256K context update loaded successfully and returned final `content=OK`.
- Observed 256K VRAM settled at about `14860 MiB` of `20475 MiB`.
- 256K probe timings were about `26.2 tok/s` prompt evaluation and `12.5 tok/s` generation.
- Live config was left at `--n-cpu-moe 40` and `--ctx-size 262144`.

Needs validation:

- Validate an agent-style coding workload against `qwen3.5-122b-a10b-mtp` at `--n-cpu-moe 40` and 256K context before treating it as the preferred local-agent default.
- Validate whether the apparent prompt evaluation improvement holds on larger prompts or is just small-prompt variance.

Tracking issue: [#117](https://github.com/alucero270/pantheon/issues/117)

### 2026-05-24 qwen122 MTP UD-IQ4_XS replacement

Live path: `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml`

Rollback snapshot created on Prometheus:

- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260523T231613Z.remove-nonmtp-qwen122-prepare-udiq4-mtp.bak`

Live model paths:

- `/mnt/local/nvme/ai/models/unsloth/Qwen3.5-122B-A10B-MTP-GGUF/Qwen3.5-122B-A10B-UD-IQ3_XXS.gguf`
- `/mnt/local/nvme/ai/models/unsloth/Qwen3.5-122B-A10B-MTP-GGUF/UD-IQ4_XS/Qwen3.5-122B-A10B-UD-IQ4_XS-00001-of-00003.gguf`
- `/mnt/local/nvme/ai/models/unsloth/Qwen3.5-122B-A10B-MTP-GGUF/UD-IQ4_XS/Qwen3.5-122B-A10B-UD-IQ4_XS-00002-of-00003.gguf`
- `/mnt/local/nvme/ai/models/unsloth/Qwen3.5-122B-A10B-MTP-GGUF/UD-IQ4_XS/Qwen3.5-122B-A10B-UD-IQ4_XS-00003-of-00003.gguf`

Changes:

- Removed the non-MTP `qwen3.5-122b-a10b` profile from the live llama-swap config.
- Removed the non-MTP UD-IQ4_XS model directory from `/mnt/local/nvme/ai/models/gguf`.
- Downloaded the MTP `UD-IQ4_XS` split GGUF files from `unsloth/Qwen3.5-122B-A10B-MTP-GGUF`.
- Materialized both the existing MTP `UD-IQ3_XXS` file and new `UD-IQ4_XS` split files as real files under `/mnt/local/nvme/ai/models/unsloth/Qwen3.5-122B-A10B-MTP-GGUF`; no model file remains as a Hugging Face cache symlink.
- Removed the accidental `/mnt/local/nvme/ai/cache` path after materializing the files.
- Updated `qwen3.5-122b-a10b-mtp` to use the `UD-IQ4_XS` first split for both `--model` and `--model-draft`.
- Preserved the tested MTP runtime settings: `--n-cpu-moe 40`, `--ctx-size 262144`, `--batch-size 4096`, `--ubatch-size 512`, `--reasoning-budget 64`, `--spec-type nextn`.

Validation result:

- `llama-swap.service` restarted successfully.
- `qwen3.5-122b-a10b-mtp` launched from the real `/mnt/local/nvme/ai/models/.../UD-IQ4_XS/...00001-of-00003.gguf` path.
- OpenAI-compatible probe returned final `content=OK`.
- Observed VRAM settled at about `18352 MiB` of `20475 MiB`.
- Probe timings were about `20.8 tok/s` prompt evaluation and `10.6 tok/s` generation.
- Post-cleanup storage: `/` had about `60G` free; `/mnt/local/nvme` had about `98G` free; the Qwen MTP model directory used about `103G`.

Needs validation:

- Validate a real agent coding workload against the MTP `UD-IQ4_XS` profile before making it the preferred default.
- Compare agent-loop reliability and wall time against the prior MTP `UD-IQ3_XXS` profile.

Tracking issue: [#117](https://github.com/alucero270/pantheon/issues/117)

### 2026-05-24 qwen122 MTP cache tuning

Live path: `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml`

Rollback snapshot created on Prometheus:

- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260524T074241Z.qwen122-mtp-cache-tuning.bak`

Tested changes:

- Model ID: `qwen3.5-122b-a10b-mtp`
- Added `--cache-ram 16384`
- Added `--ctx-checkpoints 64`
- Added `--checkpoint-every-n-tokens 4096`

Validation result:

- `llama-swap.service` restarted successfully.
- The active backend launched with the new cache flags.
- An oversized synthetic cache probe was cancelled by the client after 15 minutes and produced HTTP 502 at llama-swap, but the backend showed the expected new checkpoint behavior: 64 checkpoint capacity and checkpoints every 4096 tokens.
- After clearing the oversized probe state with a service restart, a smaller same-prefix cache probe completed successfully.
- Same-prefix probe first pass: `7667` prompt tokens, about `74.4s` prompt eval, `103 tok/s` prompt evaluation, `10.7 tok/s` generation, `81.8s` wall time.
- Same-prefix probe second pass: `7667` prompt tokens, about `5.6s` prompt eval, `93 tok/s` prompt evaluation, `10.5 tok/s` generation, `12.1s` wall time.
- Post-test health check: `llama-swap.service` active, backend health `OK`, MTP UD-IQ4_XS resident with about `18370 MiB` VRAM used and `0%` GPU utilization while idle.

Notes:

- The cache tuning helps when the prompt prefix is stable enough for reuse.
- It does not eliminate full prompt reprocessing for divergent prompt histories or hybrid/recurrent cache limitations.
- Client timeouts around 5 minutes can still make long first-pass prompts look failed even when the backend is healthy.

Needs validation:

- Validate the tuned cache settings with a real coding-agent loop instead of synthetic prompts.
- Confirm the client timeout for agent traffic is long enough for first-pass prompts above roughly 20k tokens.

Tracking issue: [#117](https://github.com/alucero270/pantheon/issues/117)

### 2026-05-22 qwen122 MTP OpenCode tuning

Live path: `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml`

Rollback snapshots created on Prometheus:

- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260522T181956Z.qwen122-timeout-reasoning.bak`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260522T183523Z.qwen122-gpu-tune.bak`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260522T183956Z.qwen122-batch4096.bak`
- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml.20260522T185120Z.qwen122-reasoning64.bak`

Current live qwen122 MTP settings after validation:

- Model ID: `qwen3.5-122b-a10b-mtp`
- `--n-cpu-moe 63`
- `--batch-size 4096`
- `--ubatch-size 512`
- `--reasoning-budget 64`

Validation result:

- `llama-swap.service` remained active.
- qwen122 MTP loaded as PID `1099418` using about `15306 MiB` GPU memory.
- Raw OpenAI-compatible request returned final `content=OK` with `max_tokens=128`.
- OpenCode JSON mode returned a `text` event containing `OK` in about `2m21s`.
- OpenCode prompt eval improved to about `79.7 tok/s` for the 8.2k-token prompt.

Notes:

- `--reasoning-budget 1024` produced reasoning-only responses under smaller completion caps, which caused OpenCode to emit no final text.
- `--batch-size 8192` did not improve the OpenCode wall time and produced an empty OpenCode text run, so it was reverted to `4096`.
- `--n-cpu-moe` below `70` did not materially increase observed VRAM beyond about `15.3 GiB`; the active VRAM use is dominated by the speculative decoding compute buffer.

### 2026-05-22 Open Design qwen122 run validation

Live path: `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml`

Rollback snapshot created on Prometheus:

- `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml..qwen122-open-design-ttl.bak`

Client-side config touched on the Windows workstation:

- `C:\Users\Alex Lucero\.config\opencode\opencode.json`

Validation result:

- Open Design spawned OpenCode with `--dir C:\Users\Alex Lucero\source\repos\huertas-jerky` and `--model llama-swap/qwen3.5-122b-a10b-mtp`.
- OpenCode first used its `small_model` for the title helper, which loaded `granite-4.1-8b` and delayed the qwen122 build request behind llama-swap's `globalTTL`.
- `small_model` was changed to `llama-swap/qwen3.5-122b-a10b-mtp` for Open Design testing so title generation does not occupy the llama-swap slot with Granite.
- `globalTTL` was temporarily lowered from `1800` to `60` to clear the unintended Granite resident model, then restored to `1800` after qwen122 loaded.
- qwen122 MTP then accepted OpenCode build-agent traffic for the `huertas-jerky` Open Design run and produced tool-loop output.
- Observed qwen122 OpenCode request timing included about `84 tok/s` prompt evaluation on a 22k-token prompt and about `7-8 tok/s` generation. Later tool-loop prompts reused enough prefix to avoid full replay in many steps, but hybrid/recurrent cache limits still caused occasional large prompt reprocessing.

Needs validation:

- Determine whether OpenCode can disable or route title generation separately for Open Design runs instead of pointing `small_model` at the same large model.
- Determine whether qwen122 MTP can use a cache mode or server option that avoids full prompt reprocessing during long OpenCode tool loops.

Tracking issue: [#117](https://github.com/alucero270/pantheon/issues/117)

## Snapshot Pattern

Before changing live config:

```bash
cp /mnt/local/nvme/ai/profiles/llama-swap/config.yaml \
  /mnt/local/nvme/ai/profiles/llama-swap/config.yaml.$(date +%F-%H%M%S).bak
```

Known-good snapshot:

```bash
cp /mnt/local/nvme/ai/profiles/llama-swap/config.yaml \
  /mnt/local/nvme/ai/profiles/llama-swap/config.yaml.known-good.$(date +%F-%H%M%S).bak
```

## Validation

```bash
curl -s -H 'Authorization: Bearer LOCAL' http://172.17.0.1:8085/v1/models
journalctl -u llama-swap.service --no-pager -n 100
nvidia-smi
```

## Rules

- Do not commit API keys, provider tokens, or secrets.
- Do not treat sanitized examples as proof of live deployment.
