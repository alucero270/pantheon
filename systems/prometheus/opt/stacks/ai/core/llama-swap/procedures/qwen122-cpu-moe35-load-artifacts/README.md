# qwen122 CPU MoE Load Artifacts

## Purpose

This folder records validation helpers used for the 2026-05-23 live load tests of `qwen3.5-122b-a10b` with lower `--n-cpu-moe` values.

## Result

`--n-cpu-moe 35` launched but failed during CUDA context initialization because the projected device memory exceeded available VRAM and the rs cache allocation failed.

`--n-cpu-moe 40` launched and served an OpenAI-compatible chat request. Small completion caps returned reasoning-only content before final `content`, so agent-style final-answer behavior still needs validation.

For the MTP profile, `--n-cpu-moe 40` launched successfully at both 128K and 256K context. The 256K test settled around `14860 MiB` of `20475 MiB` and returned final `content=OK`.

See [[systems/prometheus/opt/stacks/ai/core/llama-swap/config/README]] for the live change note, rollback snapshot, and validation result.
