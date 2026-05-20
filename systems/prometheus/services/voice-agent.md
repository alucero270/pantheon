---
type: service
service_name: voice-agent
status: planned
last_updated: 2026-05-19
---

# Voice Agent

## Purpose

The Voice Agent is the planned realtime voice interface for Pantheon AI chat on [[systems/prometheus]].

It is intended to provide a lower-latency spoken conversation loop beside [[systems/prometheus/services/openwebui]], not inside OpenWebUI itself.

Target loop:

```text
browser microphone
-> Pipecat voice agent
-> local STT service
-> [[systems/prometheus/services/llama-swap]] or [[systems/prometheus/services/ollama]]
-> local TTS service
-> browser audio playback
```

OpenWebUI remains the primary human-facing chat, model-testing, and admin UI unless a later decision changes that role.

## Hosting

- System: [[systems/prometheus]]
- Runtime: Planned Docker service or Python service
- Primary framework: Pipecat
- Candidate STT service: Speaches or another OpenAI-compatible Whisper/faster-whisper service
- Candidate TTS service: Kokoro/Piper through Speaches first; Qwen3-TTS after validation
- Compose scaffold: `systems/prometheus/automation/docker/stacks/voice-agent/compose.yml`
- Staged Prometheus copy: `/home/alex/stacks/voice-agent`
- Live compose path: `TBD`; staged copy has not been started
- Dependency: [[systems/prometheus/services/llama-swap]], [[systems/prometheus/services/ollama]], [[systems/prometheus/services/traefik]]

## Data Classification

- Authoritative: no
- Runtime: yes
- Disposable: yes by current docs

The Voice Agent must not become the sole holder of prompts, transcripts, recordings, secrets, or generated outputs. Retained outputs must follow the Atlas authority model documented in [[systems/prometheus/services/ai-runtime]].

## Storage Paths

| Path | Read/Write | Description |
|---|---|---|
| `TBD` | RW | Voice agent runtime config and cache |
| `/mnt/local/nvme/ai/models/stt/whisper/large-v3-turbo` | RO | Installed Whisper large-v3-turbo model documented for STT validation |
| `/mnt/local/nvme/ai/models/TTS/Qwen3-TTS` | RO | Installed Qwen3-TTS models documented for later TTS validation |

## Configuration

Planned components:

- Pipecat voice pipeline
- WebRTC or browser-compatible transport
- OpenAI-compatible STT endpoint
- OpenAI-compatible LLM endpoint through [[systems/prometheus/services/llama-swap]] or Ollama API through [[systems/prometheus/services/ollama]]
- OpenAI-compatible TTS endpoint

Initial target configuration:

| Component | Candidate | Status |
|---|---|---|
| Voice orchestration | Pipecat | Needs validation |
| STT | Speaches with faster-whisper | Needs validation |
| LLM | [[systems/prometheus/services/llama-swap]] | Needs validation |
| Fallback LLM | [[systems/prometheus/services/ollama]] | Needs validation |
| First TTS | Kokoro or Piper via Speaches | Needs validation |
| Later TTS | Qwen3-TTS wrapper or compatible service | Needs validation |

## Access

- URL: `voice-agent.home.arpa` is the preferred candidate if exposed through Traefik.
- Auth method: `TBD`
- Roles: `TBD`
- Public WAN exposure: disallowed by current AI runtime constraints.

Direct host port exposure should be avoided unless explicitly documented and approved.

## Security Notes

- Do not commit API keys, voice samples, transcripts, recordings, or generated user data.
- Voice cloning must not be enabled for public or commercial output without rights and consent validation.
- Browser microphone access must be limited to trusted clients.
- Access must respect Cerberus firewall policy, Traefik routing, and the SERVERS/MGMT boundary.
- Provider-backed STT/TTS/LLM services must not be introduced without a clear data-flow note.

## Backup Strategy

- Backed up: no by current docs
- Rationale: planned disposable runtime on Prometheus
- Revisit if transcripts, agent memory, custom tools, user profiles, or voice profiles become important service state.

## Monitoring & Health

Needs validation:

```bash
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | grep -E "voice-agent|speaches"
```

Candidate health checks:

- Pipecat process is running.
- STT endpoint lists or loads the expected Whisper model.
- TTS endpoint returns playable audio.
- LLM endpoint responds through [[systems/prometheus/services/llama-swap]] or [[systems/prometheus/services/ollama]].
- Browser voice loop completes microphone input to spoken response.

## Upgrade Strategy

- Pin known-good container images or Python package versions after first successful validation.
- Keep provider/model swaps explicit in docs.
- Do not promote to production-facing service until access, auth, state, and recovery posture are decided.

## Known Issues

- Needs validation under GitHub issue #110.
- Pipecat is not documented as deployed in Pantheon yet.
- Speaches is not documented as deployed in Pantheon yet.
- Voice-agent scaffold was copied to `/home/alex/stacks/voice-agent` on Prometheus on 2026-05-19, but no container start is documented from that copy.
- Qwen3-TTS is installed for ComfyUI-oriented workflows, but direct realtime TTS service use is not validated.
- OpenWebUI voice settings are separate from this service and should not be treated as the realtime voice-agent path.

## Related Docs

- Services: [[systems/prometheus/services/ai-runtime]], [[systems/prometheus/services/openwebui]], [[systems/prometheus/services/llama-swap]], [[systems/prometheus/services/ollama]], [[systems/prometheus/services/comfyui]], [[systems/prometheus/services/traefik]]
- Procedures: [[systems/prometheus/procedures/voice-agent-bootstrap]], [[systems/prometheus/procedures/comfyui-creative-production-workflow]]
- Architecture: [[systems/prometheus/architecture/compose-registry]], [[systems/network/architecture/ingress-flow]]
- Automation: [[systems/prometheus/automation/docker/stacks/voice-agent/README]]

## External References

- [Pipecat documentation](https://docs.pipecat.ai/)
- [Pipecat quickstart](https://docs.pipecat.ai/pipecat/get-started/quickstart)
- [Speaches documentation](https://speaches.ai/)
- [Speaches OpenWebUI integration](https://speaches.ai/usage/open-webui-integration/)

## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Prometheus |
| Host/system/device owner | Prometheus |
| Runtime type | Planned voice agent service |
| Source of truth | This document and [[systems/prometheus/procedures/voice-agent-bootstrap]] until validated |
| Config path | `TBD` |
| Data path | Runtime/disposable local paths only |
| Secret requirements | Do not commit API keys, voice samples, transcripts, recordings, or provider tokens |
| Network ports | Needs validation; prefer Traefik route `voice-agent.home.arpa` and no direct host port |
| Dependencies | Pipecat, STT service, TTS service, [[systems/prometheus/services/llama-swap]] or [[systems/prometheus/services/ollama]], Docker, [[systems/prometheus/services/traefik]] |
| Backup requirement | No current backup; revisit if state becomes important |
| Validation command | Needs validation |
| Recovery procedure | [[systems/prometheus/procedures/voice-agent-bootstrap]] |
| Automation classification | Candidate after manual validation |
| Preferred automation tool | Ansible after compose layout and secrets handling are normalized |
