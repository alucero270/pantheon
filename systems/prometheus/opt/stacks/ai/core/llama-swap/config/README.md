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
