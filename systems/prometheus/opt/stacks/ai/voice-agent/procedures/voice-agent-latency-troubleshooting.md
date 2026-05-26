---
type: procedure
risk_level: medium
last_tested: Unknown
---

# Voice Agent Latency Troubleshooting

## Purpose

Troubleshoot high latency in the Pipecat-based [[systems/prometheus/opt/stacks/ai/voice-agent/voice-agent]] without relying on ad-hoc package patches or untracked root-level scripts.

This procedure is for the installed validation service on [[systems/prometheus]]. It does not promote the voice-agent to production, and it does not approve public exposure.

## Current Problem

Observed issue:

- Realtime conversation has large pauses between user speech and assistant speech.
- Reported response delays are approximately 10-30 seconds.
- Earlier troubleshooting focused on Qwen3-TTS internals and created many temporary scripts.

Current hypothesis:

- The stock Qwen3-TTS generation path is a major latency contributor.
- The qwen3-tts-triton / faster-qwen3-tts hybrid backend may be fast enough for realtime validation without patching installed `site-packages`.
- Browser fatal errors during SmallWebRTC testing can come from LAN HTTP access because microphone/WebRTC APIs require HTTPS or localhost.

Status: Partially validated on 2026-05-21; end-to-end service still needs a documented HTTPS/access decision before production use. Follow-up optimization, feature exploration, and access hardening are tracked under GitHub issue #115. On-demand deployment and teardown automation is tracked under GitHub issue #116.

## 2026-05-21 Clean Baseline

Live validation on Prometheus after restoring `qwen-tts==0.1.1` and removing the ad-hoc code predictor patch from `site-packages`:

| Component | Result |
|---|---|
| Voice API startup | Healthy on `127.0.0.1:8002`; model startup about 9.8 seconds |
| GPU memory after clean start | Qwen3-TTS Voice API about 7.6 GiB VRAM |
| LLM model for voice test | `granite-4.1-8b` through [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]] |
| First component timing run | TTS 14.3s; LLM 18.1s including CPU model startup |
| Warm component timing run | TTS 8.3s; LLM 4.0s |
| TTS -> STT check | TTS 7.0s; STT 1.8s |
| Pipecat client page | `http://<prometheus-ip>:7860/client/` returned HTTP 200 |
| Pipecat voice-loop log | Shows TTS TTFB around 10.4s for a short response; end-to-end user-to-bot latency around 16.2s |
| FlashAttention 2 | Installed and loads with `QWEN_ATTN_IMPLEMENTATION=flash_attention_2`; startup improved to about 8.6 seconds |
| FlashAttention short utterance | `Hello.` measured about 3.2s default and 2.8s with `non_streaming_mode=False` |
| FlashAttention normal utterance | `I am here and ready to help.` measured about 7.8s default |
| `non_streaming_mode=False` | Not useful for normal voice replies in this environment; the same normal utterance measured about 28.1s |
| Tuned `non_streaming_mode=False` | Reduced the bad streaming-mode case but still measured about 8.5s for the normal utterance |
| Long utterance GPU sampling | GPU utilization stayed roughly 11-17% at about 36W during generation |
| Installed faster TTS fallback | No `piper`, `kokoro`, Coqui `TTS`, or `faster_qwen3_tts` package found in the voice-agent environment |
| Granite 8B GPU | `granite-4.1-8b-gpu` fits beside Qwen3-TTS; warm test about 0.19-0.36s |
| Qwen 9B GPU | `qwen3.5-9b-gpu` fits beside Qwen3-TTS; warm test about 0.95s and returned empty content in the quick voice prompt test |
| Supertonic 3 | `supertonic==1.3.1` installed in `/home/alex/stacks/voice-agent/venv` on 2026-05-24; model load and synthesis not tested because GPU was in active use |

Conclusion:

- The immediate blocker is not Pipecat configuration.
- The primary steady-state bottleneck is Qwen3-TTS generation latency.
- The local Qwen3-TTS path appears Python/HF-generation bound rather than GPU-throughput bound: GPU utilization remains low during long generation.
- The previous 27B GPU llama-swap model prevented Qwen3-TTS from loading because it occupied almost all VRAM. For voice-agent testing, use CPU `granite-4.1-8b` or another low-VRAM LLM while Qwen3-TTS is resident.
- `granite-4.1-8b-gpu` is the preferred voice-agent LLM candidate over `qwen3.5-9b-gpu` based on warm latency.
- Do not resume package patching until a documented Qwen-specific profiling pass is created.

## 2026-05-21 Hybrid Backend Validation

Live validation on Prometheus after installing `qwen3-tts-triton==0.2.0` and `faster-qwen3-tts==0.2.6` into `/home/alex/stacks/voice-agent/venv`:

| Component | Result |
|---|---|
| Voice API backend | `QWEN_TTS_BACKEND=hybrid` using `TritonFasterRunner` |
| Startup | About 14.1 seconds total; Qwen hybrid load about 6.8 seconds; prewarm/CUDA graph capture about 4.9 seconds; Whisper load about 2.4 seconds |
| TTS `OK.` | About 0.38 seconds through `systems/prometheus/opt/stacks/ai/voice-agent/config/validate_pipeline.py` |
| TTS short sentence | About 1.07 seconds for `This is a short voice latency test.` |
| TTS normal sentence | About 1.9 seconds for `I am here and ready to help.` |
| Pipecat startup reply | About 2.65 seconds TTS generation for a 100-character reply |
| Pipecat user turn | STT about 0.62 seconds, LLM about 0.38 seconds, TTS about 2.67 seconds for a 105-character reply |
| LLM | `granite-4.1-8b-gpu`; validated warm voice-turn response under 1 second |
| Browser path | `http://localhost:7860/client/` through SSH tunnel validated; LAN HTTP access can fail because it is not a browser secure context |

Conclusion:

- Qwen3-TTS itself is not rejected; the stock `qwen-tts` generation path is the latency problem.
- Keep the clean server wrapper and backend switch. Do not reintroduce ad-hoc patches under `venv/lib/python3.12/site-packages`.
- Use `granite-4.1-8b-gpu` for voice turns while Qwen3-TTS is resident.
- Keep `VOICE_AGENT_TTS_VOICE=alloy` for Pipecat `OpenAITTSService`; the Local Voice API maps it to `QWEN_SPEAKER=Ryan` internally.
- Use HTTPS through Traefik or a localhost tunnel for WebRTC validation. Do not treat a LAN HTTP fatal browser error as a Pipecat backend failure until the access path is confirmed.

## Constraints

- Do not modify live infrastructure without approval.
- Do not patch files inside `/home/alex/stacks/voice-agent/venv/lib/python3.12/site-packages` as the first troubleshooting step.
- Do not stack multiple performance patches without a baseline and before/after measurement.
- Do not commit voice samples, recordings, transcripts, generated user data, provider keys, or local `.env` files.
- Keep temporary investigation files out of the repository root.
- Use [[systems/prometheus/opt/stacks/ai/voice-agent/voice-agent]] and [[systems/prometheus/opt/stacks/ai/voice-agent/procedures/voice-agent-bootstrap]] as local context.
- Use Pipecat documentation for Pipecat runner, transport, pipeline, and service configuration questions.
- Use Qwen3-TTS documentation for Qwen model loading and generation questions.

## Evidence To Preserve

Record each test in the tracking issue or this procedure:

| Field | Value |
|---|---|
| Date/time | `TBD` |
| Host | `prometheus` |
| Git commit or working tree note | `TBD` |
| Voice API process command | `TBD` |
| Pipecat command | `TBD` |
| Qwen package version | `qwen-tts==0.1.1` per handoff; Needs validation |
| Pipecat version | `1.2.1` per service doc; Needs validation |
| GPU driver | `595.71.05` per handoff; Needs validation |
| Test text | sanitized short sentence only |
| STT latency | `TBD` |
| LLM latency | `TBD` |
| TTS first audio latency | `TBD` |
| TTS full audio latency | `TBD` |
| End-to-end turn latency | `TBD` |
| Result | `TBD` |

## Baseline First

1. Confirm clean runtime versions.

Run on Prometheus:

```bash
cd /home/alex/stacks/voice-agent
venv/bin/python3 - <<'PY'
import importlib.metadata as md
for pkg in ["pipecat-ai", "qwen-tts", "torch", "transformers", "fastapi", "uvicorn"]:
    try:
        print(pkg, md.version(pkg))
    except md.PackageNotFoundError:
        print(pkg, "not installed")
PY
```

Expected result:

- Package versions are recorded before any further changes.

2. Confirm the Voice API process and port.

```bash
pgrep -af 'voice_api_server|uvicorn'
ss -tlnp | grep ':8002'
```

Expected result:

- One expected Voice API process is listening on `127.0.0.1:8002` or the documented bind address.

3. Confirm GPU placement.

```bash
nvidia-smi
cd /home/alex/stacks/voice-agent
venv/bin/python3 - <<'PY'
import torch
print("cuda_available", torch.cuda.is_available())
print("device_count", torch.cuda.device_count())
if torch.cuda.is_available():
    print("device", torch.cuda.get_device_name(0))
PY
```

Expected result:

- GPU and driver state are recorded.
- If the model is not on the RTX 4000 Ada, stop and fix device placement before testing model internals.

## Measure The Pipeline In Order

Run one layer at a time. Do not patch anything until these numbers exist.

1. Measure TTS only.

```bash
cd /home/alex/stacks/voice-agent
venv/bin/python3 - <<'PY'
import time
import requests

payload = {
    "model": "tts-1",
    "input": "This is a short voice latency test.",
    "voice": "Ryan",
    "response_format": "wav",
}

t0 = time.perf_counter()
r = requests.post("http://127.0.0.1:8002/v1/audio/speech", json=payload, timeout=120)
t1 = time.perf_counter()
print("status", r.status_code)
print("bytes", len(r.content))
print("tts_full_seconds", round(t1 - t0, 3))
PY
```

Expected result:

- Full TTS generation time is recorded.
- If this alone is near 10 seconds, focus on Qwen3-TTS before Pipecat.

2. Measure STT only with a known short local test file.

Use a sanitized test file. Do not commit it.

```bash
cd /home/alex/stacks/voice-agent
venv/bin/python3 - <<'PY'
import time
import requests

path = "/tmp/voice-agent-test.wav"
t0 = time.perf_counter()
with open(path, "rb") as f:
    r = requests.post(
        "http://127.0.0.1:8002/v1/audio/transcriptions",
        files={"file": ("voice-agent-test.wav", f, "audio/wav")},
        data={"model": "whisper-1"},
        timeout=120,
    )
t1 = time.perf_counter()
print("status", r.status_code)
print("stt_seconds", round(t1 - t0, 3))
print(r.text[:300])
PY
```

Expected result:

- STT time is recorded separately from TTS.

3. Measure LLM only.

```bash
cd /home/alex/stacks/voice-agent
venv/bin/python3 - <<'PY'
import json
import time
import urllib.request

body = json.dumps({
    "model": "granite-4.1-8b",
    "messages": [{"role": "user", "content": "Reply with one short sentence."}],
    "max_tokens": 40,
}).encode()

req = urllib.request.Request(
    "http://172.17.0.1:8085/v1/chat/completions",
    data=body,
    headers={"Content-Type": "application/json", "Authorization": "Bearer LOCAL"},
)
t0 = time.perf_counter()
resp = urllib.request.urlopen(req, timeout=120)
t1 = time.perf_counter()
data = json.loads(resp.read())
print("llm_seconds", round(t1 - t0, 3))
print(data["choices"][0]["message"]["content"][:300])
PY
```

Expected result:

- LLM time is recorded separately from Pipecat and TTS.

4. Measure Pipecat browser/WebRTC turn latency only after component timing is known.

Use the Pipecat development runner pattern documented upstream:

```bash
cd /home/alex/stacks/voice-agent/pipecat-quickstart/pipecat-quickstart/server
uv run bot.py -t webrtc --host 0.0.0.0 --port 7860
```

Expected result:

- Browser connects to the development runner.
- One spoken prompt completes a full STT -> LLM -> TTS -> playback turn.
- End-to-end latency is recorded.

## Qwen3-TTS Checks

Before patching model internals, validate the official loading path and runtime assumptions.

1. Confirm model load options.

The Qwen3-TTS docs show loading CustomVoice with:

```python
Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    device_map="cuda:0",
    dtype=torch.bfloat16,
)
```

The repository Voice API at `systems/prometheus/opt/stacks/ai/voice-agent/config/voice_api_server.py` already uses the same basic `device_map` and `dtype` shape.

2. Check whether FlashAttention 2 is available before using it.

```bash
cd /home/alex/stacks/voice-agent
venv/bin/python3 - <<'PY'
import importlib.util
print("flash_attn_available", importlib.util.find_spec("flash_attn") is not None)
PY
```

If available, test `attn_implementation="flash_attention_2"` as a single isolated change and record before/after TTS time. If unavailable, do not enable it blindly.

3. Check device placement for model submodules.

```bash
cd /home/alex/stacks/voice-agent
venv/bin/python3 - <<'PY'
from qwen_tts import Qwen3TTSModel
import torch

model = Qwen3TTSModel.from_pretrained(
    "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    device_map="cuda:0",
    dtype=torch.bfloat16,
)

for name, module in model.named_modules():
    if any(part in name.lower() for part in ["talker", "predictor", "code"]):
        try:
            param = next(module.parameters())
        except StopIteration:
            continue
        print(name, param.device, param.dtype)
PY
```

Expected result:

- Talker and code predictor placement is known before investigating transfer overhead.

4. Only then profile Qwen internals.

If TTS is still the bottleneck after basic load and device checks, create one named profiling script under:

```text
systems/prometheus/opt/stacks/ai/voice-agent/procedures/voice-agent-latency-artifacts/
```

Do not use root-level `tmp_*.py` scripts. Do not edit the installed package until the profiling output shows where time is spent.

## Pipecat Configuration Checks

Use Pipecat documentation before changing bot code.

Known upstream requirements:

- Install runner support with `pipecat-ai[runner]`.
- Install WebRTC support with `pipecat-ai[webrtc]`.
- For local browser testing, run the development runner with `-t webrtc`.
- `SmallWebRTCTransport` requires a WebRTC connection supplied by the runner or a separate signaling server.
- HTTPS is required for production browser microphone access. Localhost is a browser exception; LAN HTTP behavior must be validated.
- ICE servers are optional on a same-LAN test, but may be needed across network boundaries.

Check the bot for:

- correct import paths for the installed Pipecat version
- `SmallWebRTCRunnerArguments` path matching the runner
- `TransportParams(audio_in_enabled=True, audio_out_enabled=True)`
- no forced startup prompt unless intentional
- metrics enabled only if useful for measurement
- no provider-backed services unless documented

## Decision Points

After baseline measurement:

| Finding | Next action |
|---|---|
| TTS alone is slow | Optimize or replace Qwen3-TTS path before changing Pipecat |
| STT is slow | Consider faster-whisper or a separate STT service |
| LLM is slow | Switch to a faster llama-swap model for voice turns |
| Pipecat adds large overhead after components are fast | Debug transport, VAD, aggregators, and runner configuration |
| Qwen3-TTS remains too slow for short turns or consumes too much GPU memory | Evaluate Supertonic 3, Piper, Kokoro, XTTS, or another local TTS fallback |

Current decision pressure:

- Qwen3-TTS remains the preferred current custom-voice path if the hybrid backend stays stable.
- Supertonic 3 is now an installed but unvalidated fallback candidate. It may offer CPU-friendly local TTS, but custom voice/style creation needs validation before it can replace Qwen3-TTS CustomVoice.
- Piper or Kokoro can remain fallback candidates, but custom voice/cloning requirements make them less direct replacements than fixing the Qwen runtime path.
- Keep FlashAttention enabled for the Qwen validation service, but do not expect it to solve realtime latency by itself.

## Cleanup Requirements

Before handing back work:

1. Run `git status --short`.
2. Move useful root-level scratch scripts into `systems/prometheus/opt/stacks/ai/voice-agent/procedures/voice-agent-latency-artifacts/` or summarize and remove them.
3. Keep at most one reusable validation script for each purpose:
   - component timing
   - end-to-end pipeline timing
   - Qwen internals profiling
4. Update [[systems/prometheus/opt/stacks/ai/voice-agent/voice-agent]] with only validated facts.
5. Update this procedure with known bottlenecks and the next test.

## Related Docs

- [[systems/prometheus/opt/stacks/ai/voice-agent/voice-agent]]
- [[systems/prometheus/opt/stacks/ai/voice-agent/procedures/voice-agent-bootstrap]]
- [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]]
- [[systems/prometheus/opt/stacks/ai/core/ai-runtime/ai-runtime]]
- [[systems/network/architecture/ingress-flow]]
- [Pipecat development runner](https://docs.pipecat.ai/server/utilities/runner/guide)
- [Pipecat SmallWebRTCTransport](https://docs.pipecat.ai/server/services/transport/small-webrtc)
- [Qwen3-TTS README](https://github.com/QwenLM/Qwen3-TTS)
- [Qwen3-TTS documentation](https://qwenlm-qwen3-tts.mintlify.app/)
