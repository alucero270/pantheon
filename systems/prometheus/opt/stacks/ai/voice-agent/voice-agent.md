---
type: service
service_name: voice-agent
status: installed, needs validation
last_updated: 2026-05-21
---

# Voice Agent

## Purpose

The Voice Agent is an installed validation service for a realtime voice interface for Pantheon AI chat on [[systems/prometheus]].

It is intended to run as a low-latency spoken conversation loop beside [[systems/prometheus/opt/stacks/ai/core/openwebui/openwebui]], not inside OpenWebUI itself.

Target loop:

```text
browser microphone
-> Pipecat voice agent
-> Local Voice API: OpenAI-compatible Whisper STT
-> [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]]
-> Local Voice API: OpenAI-compatible Qwen3-TTS
-> browser audio playback
```

OpenWebUI remains the primary human-facing chat, model-testing, and admin UI unless a later decision changes that role.

## Hosting

- System: [[systems/prometheus]]
- Runtime: Python service (uvicorn)
- Primary framework: Pipecat (voice pipeline) + Local Voice API (STT/TTS)
- STT service: Whisper large-v3-turbo via Local Voice API on port 8002
- TTS service: Qwen3-TTS 1.7B-CustomVoice via Local Voice API on port 8002
- LLM service: [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]] on `172.17.0.1:8085`
- Pipecat bot path: `/home/alex/stacks/voice-agent/pipecat-quickstart/pipecat-quickstart/server/bot.py`
- Voice API server path: `/home/alex/stacks/voice-agent/voice_api_server.py`
- Init system: `nohup` (systemd service unit provided but needs `sudo` to install)
- Compose scaffold: `systems/prometheus/automation/docker/stacks/voice-agent/compose.yml` (not used; Python-based deployment instead)
- Dependency: [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]], [[systems/prometheus/opt/stacks/ingress/traefik/traefik]]

## Data Classification

- Authoritative: no
- Runtime: yes
- Disposable: yes by current docs

The Voice Agent must not become the sole holder of prompts, transcripts, recordings, secrets, or generated outputs. Retained outputs must follow the Atlas authority model documented in [[systems/prometheus/opt/stacks/ai/core/ai-runtime/ai-runtime]].

## Storage Paths

| Path | Read/Write | Description |
|---|---|---|
| `/home/alex/stacks/voice-agent` | RW | Voice agent runtime: API server, bot.py, venv, logs |
| `/home/alex/stacks/voice-agent/voice_api_server.log` | RW | Local Voice API runtime log |
| `/mnt/local/nvme/ai/models/stt/whisper/large-v3-turbo` | RO | Installed Whisper large-v3-turbo model (HuggingFace transformers format) |
| `/mnt/local/nvme/ai/models/TTS/Qwen3-TTS` | RO | Installed Qwen3-TTS models (CustomVoice, VoiceDesign, Base) |

## Configuration

Planned components:

- Pipecat voice pipeline
- WebRTC or browser-compatible transport
- OpenAI-compatible STT endpoint
- OpenAI-compatible LLM endpoint through [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]] or Ollama API through [[systems/prometheus/opt/stacks/ai/core/ollama/ollama]]
- OpenAI-compatible TTS endpoint

Current configuration (component validation started 2026-05-21):

| Component | Service | Endpoint | Status |
|---|---|---|---|
| Voice orchestration | Pipecat 1.2.1 | SmallWebRTC transport | End-to-end WebRTC turn validated through localhost SSH tunnel on 2026-05-21 |
| STT | Whisper large-v3-turbo | `POST /v1/audio/transcriptions` on `127.0.0.1:8002` | Validated |
| LLM | [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]] (granite-4.1-8b-gpu) | `172.17.0.1:8085/v1` via OpenAILLMService | Preferred current voice candidate |
| TTS | Qwen3-TTS 1.7B-CustomVoice (Ryan voice) with `QWEN_TTS_BACKEND=hybrid` | `POST /v1/audio/speech` on `127.0.0.1:8002` | Validated with qwen3-tts-triton / faster-qwen3-tts |

## Access

- URL: `voice-agent.home.arpa` is the preferred candidate if exposed through Traefik.
- Auth method: `TBD`
- Roles: `TBD`
- Public WAN exposure: disallowed by current AI runtime constraints.

Direct host port exposure should be avoided unless explicitly documented and approved.

For current manual WebRTC validation, use an SSH tunnel and open the browser at `http://localhost:7860/client/`. Browsers treat localhost as a secure context for microphone/WebRTC testing. LAN HTTP URLs such as `http://prometheus:7860/client/` can fail or show fatal client errors because browser microphone APIs require HTTPS outside localhost.

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

```bash
# Check voice API server
pgrep -f voice_api_server && ss -tln | grep 8002

# Test TTS endpoint
python3 -c "import requests; r=requests.post('http://127.0.0.1:8002/v1/audio/speech', json={'model':'tts-1','input':'Health check','voice':'Ryan'}); print('TTS:', 'OK' if r.status_code==200 else 'FAIL')"

# Test STT endpoint
python3 -c "import requests; r=requests.post('http://127.0.0.1:8002/v1/audio/transcriptions', files={'file': ('test.wav', b'', 'audio/wav')}, data={'model':'whisper-1'}); print('STT:', 'OK' if r.status_code==200 else 'FAIL')"

# Test LLM endpoint through llama-swap
python3 -c "
import json, urllib.request
data = json.dumps({'model':'granite-4.1-8b','messages':[{'role':'user','content':'ping'}]}).encode()
req = urllib.request.Request('http://172.17.0.1:8085/v1/chat/completions', data=data, headers={'Content-Type':'application/json','Authorization':'Bearer LOCAL'})
resp = urllib.request.urlopen(req, timeout=30)
print('LLM:', 'OK' if json.loads(resp.read())['choices'][0]['message']['content'] else 'FAIL')
"
```

## Upgrade Strategy

- Pin known-good container images or Python package versions after first successful validation.
- Keep provider/model swaps explicit in docs.
- Do not promote to production-facing service until access, auth, state, and recovery posture are decided.

## Known Issues

- Validation tracked under GitHub issue #110.
- Realtime testing initially reported large pauses and 10-30 second response delays; clean baseline on 2026-05-21 measured the stock Qwen3-TTS path as the primary bottleneck with about 8-10 seconds TTS latency for short responses.
- `QWEN_TTS_BACKEND=hybrid` with qwen3-tts-triton / faster-qwen3-tts reduced validated TTS latency to about 0.38 seconds for `OK.`, about 1.07 seconds for a short sentence, and about 2.67 seconds for a 105-character Pipecat reply.
- LAN HTTP access to the SmallWebRTC client can fail because browsers require HTTPS or localhost for microphone/WebRTC APIs. Use an SSH tunnel to `localhost:7860` for manual validation until Traefik HTTPS access is documented and approved.
- Qwen3-TTS and large GPU llama-swap models cannot coexist on the RTX 4000 Ada; `granite-4.1-8b-gpu` does fit beside Qwen3-TTS and is faster than `qwen3.5-9b-gpu` in warm voice-prompt testing.
- Voice API server runs as `nohup` process; systemd unit `voice-api.service` is provided but needs `sudo` to install.
- GPU VRAM usage with `granite-4.1-8b-gpu` plus hybrid Qwen3-TTS is within RTX 4000 Ada capacity, but leaves limited headroom for additional GPU services.
- Voice API server loads both Qwen3-TTS and Whisper on startup; hybrid backend startup measured about 14.1 seconds with prewarm/CUDA graph capture.
- Speaches Docker compose exists but is not used; the unified Python server replaces it.
- OpenWebUI voice settings are separate from this service and should not be treated as the realtime voice-agent path.

## Related Docs

- Services: [[systems/prometheus/opt/stacks/ai/core/ai-runtime/ai-runtime]], [[systems/prometheus/opt/stacks/ai/core/openwebui/openwebui]], [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]], [[systems/prometheus/opt/stacks/ai/core/ollama/ollama]], [[systems/prometheus/opt/stacks/ai/core/comfyui/comfyui]], [[systems/prometheus/opt/stacks/ingress/traefik/traefik]]
- Procedures: [[systems/prometheus/opt/stacks/ai/voice-agent/procedures/voice-agent-bootstrap]], [[systems/prometheus/opt/stacks/ai/voice-agent/procedures/voice-agent-latency-troubleshooting]], [[systems/prometheus/opt/stacks/ai/core/comfyui/procedures/comfyui-creative-production-workflow]]
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
| Runtime type | Python service (uvicorn) |
| Source of truth | This document |
| Config path | `/home/alex/stacks/voice-agent/voice_api_server.py` |
| Data path | `/home/alex/stacks/voice-agent` (runtime/disposable) |
| Secret requirements | Do not commit API keys, voice samples, transcripts, recordings, or provider tokens |
| Network ports | `127.0.0.1:8002` (voice API, host-local); `172.17.0.1:8085` (llama-swap, Docker bridge) |
| Dependencies | Pipecat, Local Voice API, [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]], [[systems/prometheus/opt/stacks/ingress/traefik/traefik]] |
| Backup requirement | No current backup; revisit if state becomes important |
| Validation command | See Monitoring & Health section above |
| Recovery procedure | [[systems/prometheus/opt/stacks/ai/voice-agent/procedures/voice-agent-bootstrap]] |
| Automation classification | Candidate after manual validation |
| Preferred automation tool | Ansible after compose layout and secrets handling are normalized |
