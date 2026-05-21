# Config Versioning and Restore

## Purpose

Define the Prometheus workflow for safely versioning live runtime config files while keeping Git-backed config sanitized and recoverable.

This procedure supports issue #114.

## Model

Prometheus uses two config layers:

| Layer | Location | Purpose | Git status |
|---|---|---|---|
| Sanitized desired config | Service-owned `config/` folders under `systems/prometheus/opt/stacks` | Rebuild reference, examples, restore notes, automation inputs | Git-tracked after secret review |
| Live rollback snapshots | Beside the live config file on Prometheus | Fast rollback before and after experiments | Not Git-tracked |

## Rules

- Do not commit secrets, API keys, tokens, private voice samples, transcripts, generated user data, or host-only sensitive values.
- Do not mark a config authoritative until source-of-truth ownership is decided.
- Keep config documentation under the service folder that owns the config.
- Take a timestamped live snapshot before risky edits.
- Record validation and rollback commands next to the service-specific config notes.

## Snapshot Pattern

Before changing a live config:

```bash
cp /path/to/config /path/to/config.$(date +%F-%H%M%S).bak
```

For known-good snapshots:

```bash
cp /path/to/config /path/to/config.known-good.$(date +%F-%H%M%S).bak
```

Restore a known-good config:

```bash
cp /path/to/config.known-good.TIMESTAMP.bak /path/to/config
```

Restart or reload only according to the owning service procedure.

## Initial Prometheus Config Targets

| Service | Config notes |
|---|---|
| [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]] | [[systems/prometheus/opt/stacks/ai/core/llama-swap/config/README]] |
| [[systems/prometheus/opt/stacks/ai/core/llamacpp/llamacpp]] | [[systems/prometheus/opt/stacks/ai/core/llamacpp/config/README]] |
| [[systems/prometheus/opt/stacks/ingress/traefik/traefik]] | [[systems/prometheus/opt/stacks/ingress/traefik/config/README]] |
| [[systems/prometheus/opt/stacks/ai/core/comfyui/comfyui]] | [[systems/prometheus/opt/stacks/ai/core/comfyui/config/README]] |
| [[systems/prometheus/opt/stacks/ai/voice-agent/voice-agent]] | [[systems/prometheus/opt/stacks/ai/voice-agent/config/README]] |

## Validation

After updating service-specific config docs:

```bash
git diff --check
```

Validate the owning service with its service-specific procedure before marking a config recovery path complete.

## Stop Points

- Do not apply generated config to Prometheus without an approved live-change procedure.
- Do not move secrets into Git.
- Do not prune live snapshots until retention and ownership are documented.
- Do not treat a sanitized config example as proof of live deployment.
