# Prometheus Voice Agent Stack Scaffold

## Status

status: scaffold for issue #110

## Purpose

This folder starts the install path for the planned [[systems/prometheus/services/voice-agent]].

The first deployable component is Speaches, an OpenAI-compatible speech API service for validating local STT/TTS before wiring a full Pipecat voice loop.

This scaffold does not modify the live AI stack at `/home/alex/stacks/ai/docker-compose.yml`.

## Target Components

| Component | Status | Notes |
|---|---|---|
| Speaches | Scaffolded | First STT/TTS API validation service |
| Pipecat | Manual quickstart pending | Use `uv` and Pipecat CLI on Prometheus |
| llama-swap | Existing live dependency | Preferred OpenAI-compatible LLM endpoint |
| Ollama | Existing live fallback | Fallback LLM runtime |
| Traefik route | Not scaffolded yet | Add only after local validation succeeds |

## Secret Handling

- Do not commit `.env`.
- Do not commit provider keys.
- Do not commit voice samples, transcripts, recordings, or generated user data.
- Keep `.env.example` sanitized.

## Required Local File

Create this file locally on Prometheus:

```text
systems/prometheus/automation/docker/stacks/voice-agent/.env
```

Start from:

```bash
cp .env.example .env
```

Validate image choice before first live run:

- CUDA: `ghcr.io/speaches-ai/speaches:latest-cuda`
- CPU: `ghcr.io/speaches-ai/speaches:latest-cpu`

The base scaffold defaults to CPU so it can be smoke-tested without GPU passthrough. Use `compose.cuda.yml` with `SPEACHES_IMAGE=ghcr.io/speaches-ai/speaches:latest-cuda` after Docker GPU access is validated on Prometheus.

## Network Model

The scaffold binds Speaches to localhost:

```text
127.0.0.1:8000 -> speaches:8000
```

This is intentional for the first install pass. Do not expose Speaches through Traefik until the voice-agent access model is validated.

Pipecat should call Speaches over the Docker network when containerized:

```text
http://speaches:8000/v1
```

OpenWebUI can use the same endpoint only if it shares a Docker network with Speaches or a separate approved route is created.

## Speaches Validation

Run only when explicitly approved on Prometheus:

```bash
docker compose --env-file .env -f compose.yml config
docker compose --env-file .env -f compose.yml up -d speaches
docker compose --env-file .env -f compose.yml ps
curl http://127.0.0.1:${SPEACHES_PORT:-8000}/v1/models
```

CUDA validation form:

```bash
SPEACHES_IMAGE=ghcr.io/speaches-ai/speaches:latest-cuda docker compose --env-file .env -f compose.yml -f compose.cuda.yml config
SPEACHES_IMAGE=ghcr.io/speaches-ai/speaches:latest-cuda docker compose --env-file .env -f compose.yml -f compose.cuda.yml up -d speaches
```

Expected result:

- The `speaches` container starts.
- `/v1/models` responds.
- Model downloads may occur on first STT/TTS use.

## Pipecat Bootstrap

Pipecat is not shipped as a stable container in this scaffold. Bootstrap it on Prometheus with `uv` so the generated quickstart can be inspected before containerization.

Install prerequisites:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install pipecat-ai-cli
```

Create a local quickstart project outside authoritative data paths:

```bash
mkdir -p /mnt/local/ssd/ai/services/voice-agent
cd /mnt/local/ssd/ai/services/voice-agent
pipecat init quickstart
```

Use SmallWebRTC for the home-lab path. Pipecat documentation describes SmallWebRTC as the self-hosted/local-development transport.

Before running the bot, adapt the generated `.env` and bot service configuration to use:

```text
STT base URL: http://127.0.0.1:8000/v1 or http://speaches:8000/v1
LLM base URL: http://127.0.0.1:8085/v1
TTS base URL: http://127.0.0.1:8000/v1 or http://speaches:8000/v1
```

Then run:

```bash
uv sync
uv run bot.py
```

Expected Pipecat local URL:

```text
http://localhost:7860/client
```

## OpenWebUI STT Bridge

This is optional and separate from the realtime voice-agent path.

If OpenWebUI should use Speaches for STT during validation, the documented OpenWebUI settings are:

```text
Speech-to-Text Engine: OpenAI
API Base URL: http://speaches:8000/v1
API Key: non-empty placeholder
Model: Systran/faster-distil-whisper-large-v3
```

This requires Docker network reachability from OpenWebUI to Speaches and must be validated before changing live OpenWebUI settings.

## Known Limitations

- This compose file is not proof that the service is deployed.
- Image tags are floating placeholders and must be pinned after validation.
- Pipecat quickstart generation still needs to run on Prometheus.
- Qwen3-TTS is not wired yet; start with Kokoro/Piper via Speaches.
- Traefik labels are intentionally omitted until the local voice loop works.
- WebRTC access may require additional network validation.

## References

- [[systems/prometheus/services/voice-agent]]
- [[systems/prometheus/procedures/voice-agent-bootstrap]]
- [[systems/prometheus/services/openwebui]]
- [[systems/prometheus/services/llama-swap]]
- [[systems/prometheus/services/ollama]]
- [Pipecat quickstart](https://docs.pipecat.ai/pipecat/get-started/quickstart)
- [Pipecat transport selection](https://docs.pipecat.ai/client/concepts/choosing-a-transport)
- [Speaches installation](https://speaches.ai/installation/)
- [Speaches OpenWebUI integration](https://speaches.ai/usage/open-webui-integration/)
