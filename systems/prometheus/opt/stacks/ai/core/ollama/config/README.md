# Ollama Config

## Purpose

This folder tracks sanitized Ollama config notes and restore guidance.

## Live Config Candidates

| Live path | Purpose | Git posture |
|---|---|---|
| `/mnt/local/ssd/ai/modelfiles` | Curated Ollama Modelfile workspace | Sanitized Git candidate |
| `/mnt/local/nvme/ai/services/ollama` | Ollama state and model cache | Do not Git-track |

## Status

No Git-backed sanitized Ollama config has been committed here yet.

## Related Procedure

- [[systems/prometheus/opt/stacks/ai/core/ollama/procedures/ollama-model-management]]

## Rules

- Do not commit model blobs or private model-provider credentials.
- Treat model caches as rebuildable unless promoted by decision.
