# ComfyUI Config

## Purpose

This folder tracks sanitized ComfyUI config notes and restore guidance.

## Live Config Candidates

| Live path | Purpose | Git posture |
|---|---|---|
| `/mnt/local/nvme/ai/services/comfy-mnt/ComfyUI/extra_model_paths.yaml` | Shared model path mapping | Sanitized copy candidate |
| `/mnt/local/nvme/ai/services/comfy-mnt/ComfyUI/user/default/workflows` | User workflow state if present | Needs validation before Git |
| `/mnt/local/nvme/ai/services/comfy-mnt/ComfyUI/custom_nodes` | Installed node state | Inventory only unless pinned |

## Status

No Git-backed sanitized ComfyUI config has been committed here yet.

## Snapshot Pattern

Before changing live model path config:

```bash
cp /mnt/local/nvme/ai/services/comfy-mnt/ComfyUI/extra_model_paths.yaml \
  /mnt/local/nvme/ai/services/comfy-mnt/ComfyUI/extra_model_paths.yaml.$(date +%F-%H%M%S).bak
```

## Validation

Use [[systems/prometheus/opt/stacks/ai/core/comfyui/procedures/comfyui-creative-production-workflow]] and service-specific smoke tests before marking config recovery complete.

## Rules

- Do not commit generated images, videos, private inputs, or large model files.
- Do not commit config containing secrets or private external endpoints.
