# AI Runtime Config

## Purpose

This folder tracks sanitized config notes for the Prometheus AI runtime group.

## Status

No Git-backed sanitized config documented yet.

Use service-specific config folders for concrete runtime files:

- [[systems/prometheus/opt/stacks/ai/core/llama-swap/config/README]]
- [[systems/prometheus/opt/stacks/ai/core/llamacpp/config/README]]
- [[systems/prometheus/opt/stacks/ai/core/ollama/config/README]]
- [[systems/prometheus/opt/stacks/ai/core/comfyui/config/README]]
- [[systems/prometheus/opt/stacks/ai/core/openwebui/config/README]]

## Rules

- Do not commit API keys, provider tokens, prompts, transcripts, or generated user data.
- Do not mark Prometheus-local AI config authoritative until ownership is decided.
