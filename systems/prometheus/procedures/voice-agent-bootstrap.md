---
type: procedure
risk_level: medium
last_tested: Unknown
---

# Voice Agent Bootstrap

## Purpose

Prepare a validation path for a Pipecat-based realtime voice agent on [[systems/prometheus]].

This procedure is a planning and validation guide. It does not document a completed live deployment.

## Preconditions

- Access required: administrative access to [[systems/prometheus]]
- Systems impacted: [[systems/prometheus]]
- Services impacted: [[systems/prometheus/services/voice-agent]], [[systems/prometheus/services/llama-swap]], [[systems/prometheus/services/ollama]], [[systems/prometheus/services/traefik]]
- GitHub tracking: issue #110

Do not run mutating infrastructure changes without explicit approval.

## Target Architecture

```text
browser microphone
-> Pipecat browser/WebRTC transport
-> OpenAI-compatible STT endpoint
-> OpenAI-compatible LLM endpoint
-> OpenAI-compatible TTS endpoint
-> browser audio playback
```

Initial candidate stack:

| Layer | Candidate | Reason |
|---|---|---|
| Voice orchestration | Pipecat | Local-first realtime voice pipeline framework |
| STT | Speaches with faster-whisper | OpenAI-compatible API and local Whisper support |
| LLM | [[systems/prometheus/services/llama-swap]] | Existing OpenAI-compatible model switching endpoint |
| Fallback LLM | [[systems/prometheus/services/ollama]] | Existing local LLM runtime |
| First TTS | Kokoro or Piper through Speaches | Lower-risk OpenAI-compatible TTS baseline |
| Later TTS | Qwen3-TTS service wrapper | Higher-quality local TTS candidate already present on disk |

## Constraints

- Keep OpenWebUI as [[systems/prometheus/services/openwebui]], not as the realtime voice-agent runtime.
- Avoid direct host port exposure unless documented and approved.
- Use Traefik for approved user-facing access.
- Do not expose the service publicly.
- Do not store authoritative data on Prometheus.
- Do not commit secrets, transcripts, recordings, or voice samples.
- Do not enable voice cloning for public or commercial output without rights validation.

## Steps

1. Validate current AI endpoints.

```bash
curl http://127.0.0.1:8085/v1/models
curl http://127.0.0.1:11434/api/tags
```

Expected result:

- [[systems/prometheus/services/llama-swap]] returns OpenAI-compatible model metadata.
- [[systems/prometheus/services/ollama]] returns local model tags.

2. Choose the first validation workspace.

Candidate path:

```text
/mnt/local/ssd/ai/services/voice-agent
```

Status: Needs validation.

3. Prepare the scaffolded Speaches install.

Repository scaffold:

```text
systems/prometheus/automation/docker/stacks/voice-agent
```

Prometheus staged copy:

```text
/home/alex/stacks/voice-agent
```

The staged copy was created on 2026-05-19 because `/mnt/local/ssd/ai/services` is root-owned and passwordless sudo was not available from this workstation.

On Prometheus, copy `.env.example` to `.env`, validate the image choice, and render the compose config before starting anything:

```bash
cd /home/alex/stacks/voice-agent
cp .env.example .env
docker compose --env-file .env -f compose.yml config
```

4. Validate STT with Speaches or another OpenAI-compatible faster-whisper service.

Candidate model:

```text
/mnt/local/nvme/ai/models/stt/whisper/large-v3-turbo
```

Expected result:

- STT endpoint accepts an audio file.
- STT endpoint returns a transcript.
- Latency is acceptable for interactive chat.

5. Validate TTS with a low-risk baseline.

Start with Kokoro or Piper through an OpenAI-compatible service before Qwen3-TTS.

Expected result:

- TTS endpoint accepts text.
- TTS endpoint returns playable audio.
- Latency is acceptable for short assistant responses.

6. Validate Pipecat locally.

Use the Pipecat quickstart or a minimal local Pipecat app to connect:

- STT endpoint
- [[systems/prometheus/services/llama-swap]] endpoint
- TTS endpoint
- browser or local test transport

Expected result:

- A spoken user prompt becomes text.
- The selected local LLM generates a response.
- The TTS service speaks the response.

7. Decide the access model.

Preferred candidate:

```text
https://voice-agent.home.arpa
```

Needs validation:

- Traefik labels or dynamic config
- DNS entry
- authentication model
- browser microphone permissions
- firewall path from trusted clients

8. Document the validated runtime.

Update [[systems/prometheus/services/voice-agent]] with:

- compose path
- image or Python package versions
- runtime path
- network ports
- DNS name
- health checks
- rollback commands
- model IDs
- secrets handling

## Validation

Minimum success criteria:

- `curl` confirms the LLM endpoint is reachable from Prometheus.
- STT transcribes a short local audio sample.
- TTS returns playable audio for a short test sentence.
- Pipecat completes one full voice turn.
- No direct host port is required for final user access unless explicitly documented.
- No authoritative data is stored on Prometheus.

## Rollback

If a validation deployment fails:

1. Stop the candidate voice-agent and STT/TTS containers or services.
2. Remove any temporary Traefik route for `voice-agent.home.arpa`.
3. Confirm [[systems/prometheus/services/openwebui]], [[systems/prometheus/services/llama-swap]], and [[systems/prometheus/services/ollama]] still respond.
4. Preserve sanitized notes in this procedure or issue #110.

Do not delete source models or shared AI runtime paths during rollback.

## Warnings

- Voice samples, transcripts, recordings, and cloned voices may contain sensitive personal data.
- Voice cloning requires explicit rights and consent validation.
- Provider-backed STT, TTS, or LLM services change the data-flow and privacy posture.
- Browser microphone access should only be exposed to trusted clients.

## Automation Potential

- Can this be scripted: yes, after manual validation.
- Preferred tool: Ansible.
- Current classification: Candidate after compose path, secrets handling, health checks, and rollback are validated.

Do not add mutating automation until the manual validation path is proven.

## Related Docs

- Services: [[systems/prometheus/services/voice-agent]], [[systems/prometheus/services/ai-runtime]], [[systems/prometheus/services/openwebui]], [[systems/prometheus/services/llama-swap]], [[systems/prometheus/services/ollama]], [[systems/prometheus/services/comfyui]], [[systems/prometheus/services/traefik]]
- Procedures: [[systems/prometheus/procedures/ai-stack-initialization]], [[systems/prometheus/procedures/comfyui-creative-production-workflow]]
- Architecture: [[systems/prometheus/architecture/compose-registry]], [[systems/network/architecture/ingress-flow]]
- External references: [Pipecat documentation](https://docs.pipecat.ai/), [Speaches documentation](https://speaches.ai/)
