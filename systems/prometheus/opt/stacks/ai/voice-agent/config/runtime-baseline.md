# Prometheus Voice Agent Stack

## Status

status: installed validation baseline for issue #110

## Purpose

This folder contains the repository baseline for the installed [[systems/prometheus/opt/stacks/ai/voice-agent/voice-agent]] validation path on [[systems/prometheus]].

The current baseline is a Python runtime, not a Docker production deployment:

```text
Pipecat browser/WebRTC runner
-> Local Voice API on 127.0.0.1:8002
-> [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]]
-> Local Voice API on 127.0.0.1:8002
```

The Local Voice API wraps:

- Whisper large-v3-turbo for STT
- Qwen3-TTS 1.7B-CustomVoice for TTS, preferably with `QWEN_TTS_BACKEND=hybrid`

The old Speaches compose scaffold remains in this folder as an optional fallback experiment. It is not the current installed path.

## Files

| File | Purpose |
|---|---|
| `voice_api_server.py` | Clean OpenAI-compatible STT/TTS wrapper with timing headers and `/health` |
| `bot.py` | Pipecat bot using the development runner with SmallWebRTC or Daily arguments |
| `validate_pipeline.py` | Component latency measurement for Voice API and llama-swap |
| `voice-api.service` | Candidate systemd unit for the Local Voice API |
| `start-voice-api.sh` | Minimal launcher for `/home/alex/stacks/voice-agent` |
| `traefik-voice-agent.yml` | Candidate dynamic Traefik route; not approved until access/auth are validated |
| `compose.yml` | Legacy Speaches scaffold; not current runtime |
| `compose.cuda.yml` | Legacy Speaches GPU override |

## Secret Handling

- Do not commit `.env`.
- Do not commit provider keys.
- Do not commit voice samples, transcripts, recordings, or generated user data.
- Keep `.env.example` sanitized.

## Local Runtime Paths

Installed validation path on Prometheus:

```text
/home/alex/stacks/voice-agent
/home/alex/stacks/voice-agent/venv
/home/alex/stacks/voice-agent/voice_api_server.py
/home/alex/stacks/voice-agent/pipecat-quickstart/pipecat-quickstart/server/bot.py
/home/alex/stacks/voice-agent/logs
/home/alex/stacks/voice-agent/artifacts
```

Model paths:

```text
/mnt/local/nvme/ai/models/stt/whisper/large-v3-turbo
/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice
```

## Voice API Baseline

Start manually on Prometheus:

```bash
cd /home/alex/stacks/voice-agent
venv/bin/python3 voice_api_server.py
```

Candidate systemd install, only when approved:

```bash
sudo cp voice-api.service /etc/systemd/system/voice-api.service
sudo systemctl daemon-reload
sudo systemctl enable --now voice-api.service
```

Health check:

```bash
curl http://127.0.0.1:8002/health
```

## Pipecat Baseline

Run the Pipecat development runner on Prometheus:

```bash
cd /home/alex/stacks/voice-agent/pipecat-quickstart/pipecat-quickstart/server
uv run bot.py -t webrtc --host 0.0.0.0 --port 7860
```

Expected local runner URL:

```text
http://localhost:7860/client/
```

Use an SSH tunnel for current manual validation:

```bash
ssh -N -L 7860:127.0.0.1:7860 alex@prometheus
```

Browsers allow microphone/WebRTC APIs on localhost. LAN HTTP URLs such as `http://prometheus:7860/client/` may fail or show fatal client errors until HTTPS access is configured.

Use the Pipecat documentation before changing runner, transport, or service configuration.

## Latency Validation

Run component timing before patching anything:

```bash
cd /home/alex/stacks/voice-agent
venv/bin/python3 validate_pipeline.py
```

Optional STT timing with a sanitized local WAV file:

```bash
venv/bin/python3 validate_pipeline.py --stt-audio /tmp/voice-agent-test.wav
```

Expected result:

- Voice API health responds.
- TTS full generation time is measured.
- LLM response time is measured.
- STT response time is measured only when a test audio file is provided.

Continue with [[systems/prometheus/opt/stacks/ai/voice-agent/procedures/voice-agent-latency-troubleshooting]].

Clean baseline from 2026-05-21:

- Voice API startup: about 9.8 seconds.
- Warm TTS: about 8.3 seconds for a short sentence.
- STT: about 1.8 seconds on generated test speech.
- Warm CPU `granite-4.1-8b` LLM response: about 4.0 seconds.
- Pipecat client page: HTTP 200 on `/client/`.
- Pipecat voice-loop logs showed TTS TTFB around 10.4 seconds and user-to-bot latency around 16.2 seconds.

Follow-up diagnosis:

- `flash_attn` is installed and `QWEN_ATTN_IMPLEMENTATION=flash_attention_2` loads successfully.
- FlashAttention reduced tiny utterances to about 3 seconds but normal short replies still measured about 8 seconds.
- `non_streaming_mode=False` did not improve normal short replies in this local setup.
- GPU utilization during long Qwen3-TTS generation stayed low, suggesting the bottleneck is the local Qwen/HF generation path rather than raw GPU capacity.
- `granite-4.1-8b-gpu` fits beside Qwen3-TTS and is the preferred current voice-agent LLM candidate.
- `qwen3-tts-triton` / `faster-qwen3-tts` hybrid backend reduced warmed TTS to about 0.38 seconds for `OK.`, about 1.07 seconds for a short sentence, and about 2.67 seconds for a 105-character Pipecat reply.
- End-to-end Pipecat through a localhost SSH tunnel validated STT, Granite GPU LLM, and Qwen hybrid TTS in one voice turn.
- `supertonic==1.3.1` is installed in the voice-agent venv as a GPU-free TTS candidate, but model download, synthesis, latency, and quality are not validated.

## Known Limitations

- Production HTTPS access for the WebRTC client is not validated.
- Realtime testing originally reported 10-30 second response delays on the stock Qwen3-TTS path.
- Qwen3-TTS stock latency must not be addressed by patching model internals unless a documented profiling pass justifies it.
- The Local Voice API is host-local only by default.
- The Traefik route is a candidate only; access, authentication, DNS, and HTTPS microphone behavior need validation.
- Speaches compose files are legacy scaffold artifacts and are not evidence of a deployed service.

## References

- [[systems/prometheus/opt/stacks/ai/voice-agent/voice-agent]]
- [[systems/prometheus/opt/stacks/ai/voice-agent/procedures/voice-agent-bootstrap]]
- [[systems/prometheus/opt/stacks/ai/voice-agent/procedures/voice-agent-latency-troubleshooting]]
- [[systems/prometheus/opt/stacks/ai/core/openwebui/openwebui]]
- [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]]
- [[systems/prometheus/opt/stacks/ai/core/ollama/ollama]]
- [Pipecat development runner](https://docs.pipecat.ai/server/utilities/runner/guide)
- [Pipecat SmallWebRTCTransport](https://docs.pipecat.ai/server/services/transport/small-webrtc)
- [Qwen3-TTS README](https://github.com/QwenLM/Qwen3-TTS)
