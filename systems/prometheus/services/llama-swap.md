# llama-swap

Last validated: 2026-05-17

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
| Backend runtime | `/mnt/local/nvme/ai/runtimes/llama-cpp-turboquant/build/bin/llama-server` (v9080) |
| Backend port range | `19080+` (19080 avoids Traefik dashboard on `127.0.0.1:18080`) |

## Installation State

Live install validated on 2026-05-17:

- Upstream Linux amd64 release archive checksum verified before install.
- Binary installed under `/mnt/local/nvme/ai/runtimes/llama-swap`.
- `llama-swap.service` is enabled and active.
- Health endpoint returns `OK`.
- `/v1/models` lists the configured model names and aliases.

## Model Configuration

The live config launches `llama-cpp-turboquant` with turbo KV cache settings:

- `--cache-type-k turbo4`
- `--cache-type-v turbo3`

These cache types are turboquant-specific; they are not supported by upstream llama.cpp or ik_llama.cpp.

### Active models (validated 2026-05-17)

| Model ID | Status |
|---|---|
| `gemma-4-26b-a4b-it-128k` | Working — thinking model |
| `qwen3.5-122b-a10b-128k` | Configured (not yet load-tested at full context) |
| `glm-4.6v-128k` | Working |
| `glm-4.7-flash-128k` | Working — thinking model |
| `granite-4.1-30b-128k` | Configured |
| `granite-4.1-8b-128k` | Working |

### Disabled models

The following Qwen MTP models are removed from config pending non-MTP GGUF downloads. Their on-disk GGUFs are unsloth MTP variants that include SSM architecture tensors (`ssm_conv1d`) not supported by any current llama.cpp binary:

| Model ID | GGUF on disk |
|---|---|
| `qwen3.6-35b-a3b-128k` | `qwen3.6-35b-a3b-mtp-unsloth-ud-iq4-xs` |
| `qwen3.5-9b-128k` | `qwen3.5-9b-mtp-unsloth-ud-q4-k-xl` |
| `qwen3.6-27b-128k` | `qwen3.6-27b-mtp-unsloth-ud-q3-k-xl` |

Download non-MTP variants from HuggingFace (unsloth) to re-enable these slots.

## Network and Exposure

`llama-swap` is bound to Docker bridge host address `172.17.0.1:8085`.

No Traefik route is documented for this service as of 2026-05-17.

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

- [[systems/prometheus/services/llamacpp]]
- [[systems/prometheus/services/ai-runtime]]
- [[systems/prometheus/inventory]]
- [[systems/prometheus/architecture/storage-authority-map]]
