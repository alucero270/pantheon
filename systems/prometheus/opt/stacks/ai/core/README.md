# /opt/stacks/ai/core

## Purpose

This folder documents the core Prometheus AI stack.

| Field | Value |
|---|---|
| Current compose file | `/opt/stacks/ai/core/compose.yml` |
| Legacy compatibility path | `/home/alex/stacks/ai/docker-compose.yml` symlink |
| Runtime/data paths | `/mnt/local/nvme/ai`, `/mnt/local/ssd/ai` |
| Status | Active live stack; normalized on 2026-05-21 |

## Services

- [[systems/prometheus/opt/stacks/ai/core/ai-runtime/ai-runtime]]
- [[systems/prometheus/opt/stacks/ai/core/comfyui/comfyui]]
- [[systems/prometheus/opt/stacks/ai/core/ollama/ollama]]
- [[systems/prometheus/opt/stacks/ai/core/openwebui/openwebui]]
- [[systems/prometheus/opt/stacks/ai/core/llamacpp/llamacpp]]
- [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]]
- [[systems/prometheus/opt/stacks/ai/core/3d-scanning/3d-scanning]]

## Stack Procedures

- [[systems/prometheus/opt/stacks/ai/core/procedures/ai-stack-initialization]]
- [[systems/prometheus/opt/stacks/procedures/stack-source-normalization-2026-05-21]]
