# ComfyUI

Last validated: 2026-05-19

## Purpose
ComfyUI provides a node-based UI for **GPU-accelerated image and media generation** on [[systems/prometheus]].

This service is part of the Prometheus AI stack and is treated as **disposable compute** per [[systems/atlas/architecture/data-strategy]].

---

## Platform
- **Host:** [[systems/prometheus]]
- **Runtime:** Docker Engine + NVIDIA Container Toolkit
- **GPU:** NVIDIA RTX 4000 Ada Generation
- **Image:** `mmartial/comfyui-nvidia-docker:latest`
- **Compose path:** `/home/alex/stacks/ai/docker-compose.yml`

---

## Access

Live state exposes ComfyUI through [[systems/prometheus/services/traefik]].

- Host port: none published
- Container port: `8188/tcp`
- Traefik route: `https://comfy.home.arpa`
- Traefik service target: container port `8188`

Older docs described SSH-tunnel-only access. Current live state uses the Traefik Docker-provider pattern.

---

## Storage

### Data Classification
- **Disposable (runtime):** yes
- **Authoritative:** no

ComfyUI state and outputs are stored on Prometheus local disks and may be rebuilt at any time.

### Host Paths
- **ComfyUI runtime/state (NVMe):**
  - `/mnt/local/nvme/ai/services/comfy-mnt`
  Mounted into container as `/comfy/mnt`.

- **Shared models (NVMe, read-only):**
  - `/mnt/local/nvme/ai/models`

- **Outputs (SSD):**
  - `/mnt/local/ssd/ai/outputs/comfy`

### Container Paths
- **Run root:** `/comfy/mnt`
- **Models:** `/comfy/mnt/models` (implemented via symlink to a read-only mount)
- **Outputs:** `/comfy/mnt/output`
- **ComfyUI default output path:** `/comfy/mnt/ComfyUI/output` is symlinked to `/comfy/mnt/output`

### Shared Model Path

ComfyUI loads the shared model root through:

- `/mnt/local/nvme/ai/services/comfy-mnt/ComfyUI/extra_model_paths.yaml`

This file points ComfyUI model categories at `/comfy/shared-models`, which is backed by `/mnt/local/nvme/ai/models`.

The documented `/comfy/mnt/models` path contains symlinks to the same shared model categories for operator clarity.

### Creative Production Baseline

Installed on 2026-05-19:

| Capability | Models / Files | Host path |
|---|---|---|
| SD1.5 checkpoint compatibility | `v1-5-pruned-emaonly-fp16.safetensors` | `/mnt/local/nvme/ai/models/checkpoints` |
| Image generation | `qwen_image_fp8_e4m3fn.safetensors` | `/mnt/local/nvme/ai/models/diffusion_models` |
| Image editing | `qwen_image_edit_2509_fp8_e4m3fn.safetensors` | `/mnt/local/nvme/ai/models/diffusion_models` |
| Qwen Image text encoder | `qwen_2.5_vl_7b_fp8_scaled.safetensors` | `/mnt/local/nvme/ai/models/text_encoders` |
| Qwen Image VAE | `qwen_image_vae.safetensors` | `/mnt/local/nvme/ai/models/vae` |
| Video generation | `wan2.2_ti2v_5B_fp16.safetensors` | `/mnt/local/nvme/ai/models/diffusion_models` |
| Quantized Wan I2V high-noise model | `Wan2.2-I2V-A14B-HighNoise-Q4_K_M.gguf` | `/mnt/local/nvme/ai/models/unet` |
| Quantized Wan I2V low-noise model | `Wan2.2-I2V-A14B-LowNoise-Q4_K_M.gguf` | `/mnt/local/nvme/ai/models/unet` |
| LTX 2.3 distilled GGUF video model | `ltx-2.3-22b-distilled-UD-Q4_K_S.gguf` | `/mnt/local/nvme/ai/models/unet` |
| LTX 2.3 text encoder, projector, and connector | `gemma-3-12b-it-qat-UD-Q4_K_XL.gguf`, `mmproj-BF16.gguf`, `ltx-2.3-22b-distilled_embeddings_connectors.safetensors` | `/mnt/local/nvme/ai/models/text_encoders` |
| LTX 2.3 distilled VAEs | `ltx-2.3-22b-distilled_video_vae.safetensors`, `ltx-2.3-22b-distilled_audio_vae.safetensors` | `/mnt/local/nvme/ai/models/vae` |
| LTX 2.3 distilled LoRA | `ltx-2.3-22b-distilled-lora-384.safetensors` | `/mnt/local/nvme/ai/models/loras` |
| LTX 2.3 latent upscaler | `ltx-2.3-spatial-upscaler-x2-1.0.safetensors` | `/mnt/local/nvme/ai/models/latent_upscale_models` |
| Wan I2V LightX2V LoRAs | `wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors`, `wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors` | `/mnt/local/nvme/ai/models/loras` |
| Wan text encoder | `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | `/mnt/local/nvme/ai/models/text_encoders` |
| Wan VAE | `wan2.2_vae.safetensors`, `wan_2.1_vae.safetensors` | `/mnt/local/nvme/ai/models/vae` |
| Upscaling | `RealESRGAN_x4plus.pth`, `4x-UltraSharp.pth` | `/mnt/local/nvme/ai/models/upscale_models` |
| TTS / voice | Qwen3-TTS 0.6B Base, 1.7B CustomVoice, 1.7B VoiceDesign | `/mnt/local/nvme/ai/models/TTS/Qwen3-TTS` |
| STT | Whisper large-v3-turbo | `/mnt/local/nvme/ai/models/stt/whisper/large-v3-turbo` |

`4x-UltraSharp.pth` was installed for trial use; verify license suitability before commercial output.

---

## Critical Constraints

ComfyUI is deployed using the `mmartial/comfyui-nvidia-docker` image.

This image enforces strict startup validation:

- Container must run as **UID/GID 1024:1024**
- `/comfy/mnt` **must** be a single bind mount owned by 1024:1024

These constraints and the required storage layout are formalized in:

- [[decisions/ADR-006-comfyui-storage-constraints]]

---

## Deployment

ComfyUI is managed as part of the AI Docker Compose stack:

- Compose location: `~/stacks/ai/docker-compose.yml`
- Service name: `comfy`

Bring-up and troubleshooting are documented in:

- [[systems/prometheus/procedures/ai-stack-initialization]]

---

## Validation

### Service health
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "^comfy\b"
```

### HTTP reachability (on Prometheus)
```bash
curl -k --resolve comfy.home.arpa:443:127.0.0.1 https://comfy.home.arpa/
```

### GPU visible in container logs
```bash
docker logs --tail=50 comfy
```

---

## Notes

- First boot may take significant time due to PyTorch + CUDA wheel downloads.
- Keep the service bound to localhost unless explicitly designing a hardened LAN exposure model.
- Audio node imports require `torchaudio` to match the installed PyTorch CUDA build. On 2026-05-19, `torchaudio 2.11.0+cu128` was replaced with `torchaudio 2.11.0+cu130` to match `torch 2.12.0+cu130`.
- A post-install API smoke test queued `EmptyImage -> SaveImage` through `https://comfy.home.arpa/prompt` and wrote output to `/mnt/local/ssd/ai/outputs/comfy/codex_smoke`.
- A `CheckpointLoaderSimple` smoke test for `v1-5-pruned-emaonly-fp16.safetensors` completed successfully and wrote `sd15_checkpoint_smoke_00001_.png` to `/mnt/local/ssd/ai/outputs/comfy/codex_smoke`.
- Wan 2.2 I2V Q4_K_M GGUF models were installed on 2026-05-19 for lower-memory template use. Use `UnetLoaderGGUF` or `UnetLoaderGGUFAdvanced`; normal `UNETLoader` workflows that reference FP8 filenames must be adjusted.
- `ComfyUI-GGUF` expects GGUF UNET files through the `unet` model category. The `unet` category maps to `/mnt/local/nvme/ai/models/unet`; the Wan I2V GGUF entries there are symlinks to the downloaded files under `/mnt/local/nvme/ai/models/diffusion_models`.
- Wan 2.2 LightX2V single-stage LoRA tests completed successfully on 2026-05-19. High-noise-only and low-noise-only GGUF LoRA workflows produced 640x640, 81-frame, 16 fps MP4s. The original dual-LoRA graph also completed, but emitted LoRA tensor shape warnings; prefer single-stage LoRA graphs for cleaner testing.
- LTX 2.3 distilled `UD-Q4_K_S` was installed on 2026-05-19 from `unsloth/LTX-2.3-GGUF`. The active validated stack uses `DualCLIPLoaderGGUF`, `UnetLoaderGGUF`, `VAELoaderKJ`, `LoraLoaderModelOnly`, `LTXVEmptyLatentAudio`, `LTXVLatentUpsampler`, and `SaveVideo`.
- ComfyUI was reset to clean upstream source and fast-forwarded to `0.21.1` on 2026-05-19 after earlier local compatibility patches were removed. Core requirements and custom node requirements were reinstalled.
- A KJ-node LTX 2.3 GGUF + LoRA smoke path succeeded on clean ComfyUI `0.21.1` with `GGUFLoaderKJ`, `LTX2LoraLoaderAdvanced`, `LTXAVTextEncoderLoader`, `gemma_3_12B_it_fp4_mixed.safetensors`, `ltx-2.3-22b-distilled_embeddings_connectors.safetensors`, `ltx-2.3-22b-distilled-UD-Q4_K_S.gguf`, `ltx-2.3-22b-distilled-lora-384-1.1.safetensors`, and `taeltx2_3.safetensors`. Those alternate Gemma/VAE/LoRA files were removed from the active model folders after the Unsloth GGUF workflow path was selected.
- The validated Unsloth-derived LTX 2.3 UD-Q4_K_S workflow artifacts are preserved under `systems/prometheus/procedures/workflows/comfyui/`. Smoke prompt `641147e2-774f-4a97-9750-64c31ec6568c` wrote `codex_smoke/unsloth_ltx23_udq4ks_smoke_00001_.mp4`. Max-length prompt `9f8baafc-4811-4470-99d3-2f7ede7a471e` wrote `codex_max/ltx23_high_action_udq4ks_1280x720_121f_24fps_00001_.mp4`.
- The distilled LTX 2 image-to-video template is preserved at `systems/prometheus/procedures/workflows/comfyui/video_ltx2_i2v_distilled.json` as a candidate graph shape for image-to-video adaptation. It is not the validated LTX 2.3 GGUF + LoRA graph; see [[systems/prometheus/procedures/comfyui-creative-production-workflow]].


## Automation Readiness

| Field | Value |
|---|---|
| Owning domain | Prometheus |
| Host/system/device owner | Prometheus |
| Runtime type | GPU/Docker workload |
| Source of truth | [[decisions/ADR-006-comfyui-storage-constraints]] and [[systems/prometheus/procedures/ai-stack-initialization]] |
| Config path | `/home/alex/stacks/ai/docker-compose.yml` |
| Data path | `/mnt/local/nvme/ai/services/comfy-mnt`, `/mnt/local/nvme/ai/models`, `/mnt/local/ssd/ai/outputs/comfy` |
| Secret requirements | Do not commit secrets |
| Network ports | Container `8188/tcp`; Traefik route `comfy.home.arpa`; no host port |
| Dependencies | GPU runtime, Docker, local storage constraints |
| Backup requirement | No authoritative data; generated output handling needs validation before cleanup |
| Validation command | `curl -k --resolve comfy.home.arpa:443:127.0.0.1 https://comfy.home.arpa/` |
| Recovery procedure | [[systems/prometheus/procedures/ai-stack-initialization]] |
| Automation classification | Ansible candidate after GPU/runtime validation |
| Preferred automation tool | Ansible candidate after GPU/runtime validation |
