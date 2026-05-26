---
type: procedure
risk_level: medium
last_tested: Unknown
---

# Voice Agent Bootstrap

## Purpose

Prepare or recover the validation path for a Pipecat-based realtime voice agent on [[systems/prometheus]].

This procedure documents an installed validation service. It does not document a production-ready deployment.

## Preconditions

- Access required: administrative access to [[systems/prometheus]]
- Systems impacted: [[systems/prometheus]]
- Services impacted: [[systems/prometheus/opt/stacks/ai/voice-agent/voice-agent]], [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]], [[systems/prometheus/opt/stacks/ai/core/ollama/ollama]], [[systems/prometheus/opt/stacks/ingress/traefik/traefik]]
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

Current validation stack:

| Layer | Candidate | Reason |
|---|---|---|
| Voice orchestration | Pipecat | Local-first realtime voice pipeline framework |
| STT | Local Voice API with Whisper large-v3-turbo | OpenAI-compatible endpoint and local model path |
| LLM | [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]] | Existing OpenAI-compatible model switching endpoint |
| Fallback LLM | [[systems/prometheus/opt/stacks/ai/core/ollama/ollama]] | Existing local LLM runtime |
| TTS | Local Voice API with Qwen3-TTS 1.7B-CustomVoice | Installed higher-quality local TTS candidate |
| Fallback TTS | Supertonic 3, Kokoro, Piper, XTTS, or Speaches | Candidate if Qwen3-TTS latency remains too high or GPU-free TTS is preferred |

## Constraints

- Keep OpenWebUI as [[systems/prometheus/opt/stacks/ai/core/openwebui/openwebui]], not as the realtime voice-agent runtime.
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

- [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]] returns OpenAI-compatible model metadata.
- [[systems/prometheus/opt/stacks/ai/core/ollama/ollama]] returns local model tags.

2. Choose the first validation workspace.

Candidate path:

```text
/mnt/local/ssd/ai/services/voice-agent
```

Status: Needs validation.

3. Prepare the installed validation workspace.

Repository baseline:

```text
systems/prometheus/opt/stacks/ai/voice-agent/config
```

Prometheus staged copy:

```text
/home/alex/stacks/voice-agent
```

The staged copy was created on 2026-05-19 because `/mnt/local/ssd/ai/services` is root-owned and passwordless sudo was not available from this workstation.

On Prometheus, keep runtime files under the staged copy and do not store authoritative data there:

```bash
cd /home/alex/stacks/voice-agent
```

4. Validate the Local Voice API.

Start manually:

```bash
cd /home/alex/stacks/voice-agent
venv/bin/python3 voice_api_server.py
```

Expected endpoint:

```text
http://127.0.0.1:8002/health
```

5. Validate STT with the Local Voice API.

Expected result:
- STT endpoint accepts an audio file.
- STT endpoint returns a transcript.
- Latency is acceptable for interactive chat.

6. Validate TTS with Qwen3-TTS.

Use Qwen3-TTS 1.7B-CustomVoice model directly for TTS validation.

Expected result:
- TTS endpoint accepts text.
- TTS endpoint returns playable audio.
- Latency is measured and recorded using [[systems/prometheus/opt/stacks/ai/voice-agent/procedures/voice-agent-latency-troubleshooting]].

7. Validate Pipecat locally.

Use the Pipecat quickstart or a minimal local Pipecat app to connect:

- STT endpoint
- [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]] endpoint
- TTS endpoint
- browser or local test transport

Expected result:

- A spoken user prompt becomes text.
- The selected local LLM generates a response.
- The TTS service speaks the response.

8. Decide the access model.

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

9. Document the validated runtime.

Update [[systems/prometheus/opt/stacks/ai/voice-agent/voice-agent]] with:

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
- Current latency troubleshooting follows [[systems/prometheus/opt/stacks/ai/voice-agent/procedures/voice-agent-latency-troubleshooting]].

## Rollback

If a validation deployment fails:

1. Stop the candidate voice-agent and STT/TTS containers or services.
2. Remove any temporary Traefik route for `voice-agent.home.arpa`.
3. Confirm [[systems/prometheus/opt/stacks/ai/core/openwebui/openwebui]], [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]], and [[systems/prometheus/opt/stacks/ai/core/ollama/ollama]] still respond.
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

- Services: [[systems/prometheus/opt/stacks/ai/voice-agent/voice-agent]], [[systems/prometheus/opt/stacks/ai/core/ai-runtime/ai-runtime]], [[systems/prometheus/opt/stacks/ai/core/openwebui/openwebui]], [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]], [[systems/prometheus/opt/stacks/ai/core/ollama/ollama]], [[systems/prometheus/opt/stacks/ai/core/comfyui/comfyui]], [[systems/prometheus/opt/stacks/ingress/traefik/traefik]]
- Procedures: [[systems/prometheus/opt/stacks/ai/core/procedures/ai-stack-initialization]], [[systems/prometheus/opt/stacks/ai/voice-agent/procedures/voice-agent-latency-troubleshooting]], [[systems/prometheus/opt/stacks/ai/core/comfyui/procedures/comfyui-creative-production-workflow]]
- Architecture: [[systems/prometheus/architecture/compose-registry]], [[systems/network/architecture/ingress-flow]]
- External references: [Pipecat documentation](https://docs.pipecat.ai/), [Speaches documentation](https://speaches.ai/)
