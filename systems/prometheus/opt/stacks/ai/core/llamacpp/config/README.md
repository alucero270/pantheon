# llama.cpp Config

## Purpose

This folder tracks sanitized llama.cpp router config notes and restore guidance.

## Live Config Candidates

| Live path | Purpose | Git posture |
|---|---|---|
| `/mnt/local/nvme/ai/profiles/start-scripts/llama-router.sh` | Router start script | Sanitized Git candidate |
| `/mnt/local/nvme/ai/profiles/llama-router-models.ini` | Router model profile config | Sanitized Git candidate after secret review |
| `/etc/systemd/system/llamacpp-router.service` | Native service unit | Sanitized Git candidate |

## Status

No Git-backed sanitized llama.cpp router config has been committed here yet.

## Snapshot Pattern

```bash
cp /mnt/local/nvme/ai/profiles/llama-router-models.ini \
  /mnt/local/nvme/ai/profiles/llama-router-models.ini.$(date +%F-%H%M%S).bak
```

## Validation

```bash
journalctl -u llamacpp-router.service --no-pager -n 100
curl -s http://172.17.0.1:8084/v1/models
```

## Rules

- Do not commit API keys or private model paths that reveal sensitive local data.
- Do not commit model files.
