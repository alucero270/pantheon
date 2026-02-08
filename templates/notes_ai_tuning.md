---
type: notes
scope: ai
status: active
last_updated: 2026-02-02
---

# AI Tuning Notes (Prometheus)

## Purpose
Capture tuning decisions and troubleshooting outcomes for the local AI stack on [[systems/prometheus]].

This file is **notes**, not an authoritative procedure.
For the rebuild steps, see [[procedures/prometheus-ai-stack-bringup]].

---

## Current stack (high level)
- Runtime: [[services/ollama]]
- UI: [[services/openwebui]]
- Image gen: [[services/comfyui]]
- Access pattern: localhost-only + SSH tunnels

---

## Baseline constraints
- GPU: NVIDIA RTX 4000 Ada (20 GB VRAM)
- Ollama will frequently enter **low VRAM mode** on 20 GB cards.
- Large models can fail to load on GPU with:
  - `cudaMalloc failed: out of memory`
  - `unable to allocate CUDA0 buffer`

---

## Symptom patterns we observed
### 1) GPU not being used at all
- Root cause we hit: `nvidia_uvm` not loaded until restart
- Fix path:
  - `sudo modprobe nvidia_uvm`
  - if still not active: reboot

### 2) CLI works but OpenWebUI fails / hangs
Common causes:
- OpenWebUI sends different request patterns than the CLI
- Model switching + keepalive keeps a “big” model resident
- Load failures surface as `500` from Ollama and appear as a UI hang

Quick check:
- `docker logs --tail=200 ollama | tail -n 50`
- Look for: `Load failed` or `unable to allocate CUDA0 buffer`

---

## Ollama runtime knobs (what matters)

### Primary knobs
- `PARAMETER num_ctx`
  - Bigger context = more KV cache = more VRAM/RAM pressure
- `PARAMETER num_gpu`
  - Controls GPU offload.
  - Too high can trigger a full-GPU load attempt and crash.
- `PARAMETER num_batch`
  - Higher batch can increase speed but increases peak memory.

### House defaults we’re using as a starting point
- `num_batch: 256`
- `num_gpu: 19` (targeting partial offload for 20 GB cards)
- `num_ctx: tune per model`

---

## Model notes

### Deepseek 32B (stable)
Goal: keep it stable on 20 GB VRAM.

Starting point:
- `num_gpu: 19`
- `num_batch: 256`
- `num_ctx: ~3500` (adjust upward only if stable)

If it OOMs:
- drop `num_ctx` first
- then drop `num_gpu`
- then drop `num_batch`

### Qwen 30B
Observation: feels faster + better output quality in our usage.
Plan:
- treat as the default “quality” model
- tune for stability similarly (ctx first)

### Mistral-Nemo
Observation: very fast.
Plan:
- tune as the default “fast chat” model

### Mixtral / Llama 3 models
Status: candidates for removal from the stack if they remain unstable / redundant.

---

## Minimal tuning loop (repeatable)
1) Ensure a clean slate
   - stop active generation
   - optionally restart Ollama container
2) Load model once via CLI
   - confirm it loads without `Load failed`
3) Run a 2–3 minute test prompt
4) Observe:
   - `ollama ps` (processor split)
   - `nvidia-smi` (VRAM / utilization)
   - `docker logs ollama` (load details)
5) Adjust only **one** parameter at a time (ctx, gpu, batch)

---

## Useful commands
- Models:
  - `docker exec -it ollama ollama list`
- Active runners:
  - `docker exec -it ollama ollama ps`
- Ollama logs:
  - `docker logs --tail=200 ollama`
- Quick API sanity:
  - `curl -s http://127.0.0.1:11434/api/tags | head`
- GPU view:
  - `watch -n 0.5 nvidia-smi`

---

## Open questions / follow-ups
- Confirm the best long-term model set (likely: Qwen + Deepseek + Mistral-Nemo).
- Decide whether we need an explicit “router” service later or keep routing as policy/config first.
- Document RAG/CAG plan + where it plugs into the stack.

