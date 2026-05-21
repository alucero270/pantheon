# Rogue Scratch Archive - 2026-05-21

## Purpose

This folder preserves root-level scratch scripts created during the first Qwen3-TTS latency troubleshooting pass.

The files are retained as investigation evidence only. They are not an approved deployment path, validation suite, or automation scaffold.

## Important Notes

- Several scripts directly patch files under `/home/alex/stacks/voice-agent/venv/lib/python3.12/site-packages`.
- Do not run patch scripts from this folder unless the exact change has been reviewed and documented in [[systems/prometheus/opt/stacks/ai/voice-agent/procedures/voice-agent-latency-troubleshooting]].
- Prefer the clean validation script at `systems/prometheus/automation/docker/stacks/voice-agent/validate_pipeline.py` for new timing work.
- Preserve useful findings by summarizing them in [[systems/prometheus/opt/stacks/ai/voice-agent/procedures/voice-agent-latency-troubleshooting]] or issue #110.

## Cleanup Status

- Moved from repository root to this folder on 2026-05-21.
- Root-level scratch files were preserved rather than deleted.
- Baseline troubleshooting should restart from documented component timings before using any script in this archive.
