# Prometheus Service Inventory

## Purpose

This document maps Prometheus service and container inventory before cleanup, migration, or stack normalization.

No services are deleted, moved, stopped, or modified by this inventory.

## Evidence Boundary

Use repository evidence and explicitly provided validated live state only.

Rows marked `Needs validation` identify services, containers, paths, ports, or images requested for inventory but not proven by the current repository documentation or validated live-state evidence.

Direct SSH revalidation from this workstation succeeded on 2026-05-16. The media stack rows below are reconciled from live Prometheus evidence and the validated state supplied for Milestone 9.

Direct SSH revalidation for the AI, Traefik, and SearXNG state succeeded on 2026-05-17. No services were stopped, moved, deleted, or modified during that run.

## Related Docs

- [[systems/prometheus]]
- [[systems/prometheus/architecture/compose-registry]]
- [[systems/prometheus/architecture/storage-authority-map]]
- [[decisions/ADR-010-container-lifecycle-policy-prometheus]]
- [[systems/prometheus/services/README]]
- [[systems/prometheus/opt/stacks/ai/core/procedures/ai-stack-initialization]]
- [[systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy]]
- [[systems/prometheus/opt/stacks/ingress/traefik/procedures/reverse-proxy-validation]]
- [[automation/policies/automation-classification]]

## Current Path Drift

Prometheus documentation currently shows three deployment/data patterns:

| Path Pattern | Evidence | Current Meaning | Drift / Risk | Recommended Action |
|---|---|---|---|---|
| `/opt/stacks/ingress/traefik/compose.yml` | Live normalization on 2026-05-21, [[systems/prometheus/opt/stacks/ingress/traefik/README]] | Reverse proxy Compose source | Legacy path `/opt/traefik/docker-compose.yml` is a symlink; config/data remains under `/opt/traefik` | Keep; validate dashboard localhost access |
| `/opt/stacks/media/vpn/compose.yml` | Live normalization on 2026-05-21, [[systems/prometheus/opt/stacks/media/vpn/README]] | Media VPN Compose source | Legacy path `/opt/vpn/docker-compose.yml` is a symlink; secrets and runtime data remain under `/opt/vpn`, `/opt/torrents`, and `/opt/arr` | Keep; continue media validation procedure |
| `/opt/stacks/ai/core/compose.yml` | Live normalization on 2026-05-21, [[systems/prometheus/opt/stacks/ai/core/README]] | AI Docker Compose source | Legacy path `/home/alex/stacks/ai/docker-compose.yml` is a symlink; AI runtime data remains under `/mnt/local/nvme/ai` and `/mnt/local/ssd/ai` | Keep; resolve Ollama route drift |
| `/mnt/local/nvme/ai/...` | [[systems/prometheus/opt/stacks/ai/core/procedures/ai-stack-initialization]], [[systems/prometheus/opt/stacks/ai/core/ollama/ollama]], [[systems/prometheus/opt/stacks/ai/core/comfyui/comfyui]], [[systems/prometheus/opt/stacks/ai/core/llamacpp/llamacpp]], [[systems/prometheus/opt/stacks/ai/core/llama-swap/llama-swap]] | Fast local runtime/model/service data | Disposable local data, but still operationally important | Keep as local runtime path; validate ownership and mount state |
| `/mnt/local/ssd/ai/...` | [[systems/prometheus/opt/stacks/ai/core/procedures/ai-stack-initialization]], [[systems/prometheus/opt/stacks/ai/core/openwebui/openwebui]], [[systems/prometheus/opt/stacks/ai/core/comfyui/comfyui]] | Write-heavy local project/output data | Disposable local data; output handling needs validation | Keep as local runtime/output path; validate backup expectation |
| `/opt/stacks/ai/searxng/compose.yml` | Live normalization on 2026-05-21, [[systems/prometheus/opt/stacks/ai/searxng/README]] | SearXNG Compose source | Legacy path `/mnt/local/ssd/ai/services/searxng/docker-compose.yml` is a symlink; runtime config remains under `/mnt/local/ssd/ai/services/searxng` | Keep; complete OpenWebUI integration validation |

## Lifecycle Classifications

| Classification | Meaning |
|---|---|
| Active documented | Current repo documents the service as active or operational |
| Active needs validation | Requested inventory item, but repo lacks enough evidence to prove deployment details |
| Questionable / exited needs validation | Requested questionable or exited container; repo lacks live evidence |
| Disposable runtime | Data or state can be rebuilt and is not authoritative |
| Cleanup candidate | Do not remove yet; requires live validation and rollback plan |

## Active Documented Inventory

| Service / Stack | Container Name | Image | Compose Path | Host Data Paths | Container Paths | Ports / Exposure | Lifecycle Classification | Recommended Action |
|---|---|---|---|---|---|---|---|---|
| AI stack | `comfy`, `ollama`, `openwebui`; exited `gemma-192k` | Mixed; see service rows | `/opt/stacks/ai/core/compose.yml` | `/mnt/local/nvme/ai/`, `/mnt/local/ssd/ai/` | See service rows | Traefik routes for ComfyUI, OpenWebUI, and Ollama; Ollama route needs decision | Active documented / Needs access-model decision | Keep; resolve Ollama route drift before automation |
| ComfyUI | `comfy` | `mmartial/comfyui-nvidia-docker:latest` | `/opt/stacks/ai/core/compose.yml` | `/mnt/local/nvme/ai/services/comfy-mnt`, `/mnt/local/nvme/ai/models`, `/mnt/local/ssd/ai/outputs/comfy` | `/comfy/mnt`, `/comfy/shared-models`, `/comfy/mnt/output` | Traefik route `comfy.home.arpa`; no host port | Active documented / Disposable runtime; exited before 2026-05-21 source normalization | Keep; preserve UID/GID 1024:1024 constraints; creative production baseline models installed 2026-05-19 |
| llama.cpp router | `llamacpp-router.service` | Native `llama-server` from `/mnt/local/nvme/ai/runtimes/llama-cpp-turboquant` | `/etc/systemd/system/llamacpp-router.service`; `/mnt/local/nvme/ai/profiles/start-scripts/llama-router.sh`; `/mnt/local/nvme/ai/profiles/llama-router-models.ini` | `/mnt/local/nvme/ai/runtimes`, `/mnt/local/nvme/ai/models/gguf`, `/mnt/local/nvme/ai/profiles` | Not containerized | `172.17.0.1:8084`; local API key | Active documented / Disposable runtime | Keep; `ik_llama.cpp` is available for MTP validation, while `llama-cpp-turboquant` is used for turbo KV cache profiles |
| llama-swap | `llama-swap.service` | Native `llama-swap` v214 | `/etc/systemd/system/llama-swap.service`; `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml` | `/mnt/local/nvme/ai/runtimes/llama-swap`, `/mnt/local/nvme/ai/runtimes/ik_llama.cpp`, `/mnt/local/nvme/ai/models/gguf` | Not containerized | `172.17.0.1:8085`; local API key `LOCAL`; Traefik route `llama-swap.home.arpa` | Active documented / Disposable runtime | Keep; exposes one OpenWebUI-visible ID per profile; tested profiles include full-GPU Granite 30B at 80K and MoE CPU/GPU expert splits for GLM 4.6V and Qwen 122B; MiniMax and Nemotron profiles copied from known-good router presets; Qwen non-MTP profiles replace unsupported MTP profiles |
| Ollama | `ollama` | `ollama/ollama:latest` | `/opt/stacks/ai/core/compose.yml` | `/mnt/local/nvme/ai/services/ollama`, `/mnt/local/ssd/ai/modelfiles` | `/root/.ollama`, `/modelfiles` | `127.0.0.1:11434 -> 11434/tcp`; live Traefik route `ollama.home.arpa` needs decision | Active documented / Disposable runtime | Keep; decide whether to remove route or update ingress decision |
| OpenWebUI | `openwebui` | `ghcr.io/open-webui/open-webui:latest` | `/opt/stacks/ai/core/compose.yml` | `/mnt/local/ssd/ai/projects/openwebui` | `/app/backend/data` | Traefik route `openwebui.home.arpa`; no host port | Active documented / Disposable runtime by current docs | Keep; Ollama and llama-swap are enabled; web search disabled in live environment |
| SearXNG | `searxng`, `searxng-redis` | `searxng/searxng:latest`, `redis:7-alpine` | `/opt/stacks/ai/searxng/compose.yml` | `/mnt/local/ssd/ai/services/searxng/searxng`; anonymous Docker volumes for cache and Redis data | `/etc/searxng`, `/var/cache/searxng`, `/data` | Traefik route `searxng.home.arpa`; no host port; IP allowlist label present | Active documented / Persistent runtime config | Keep; complete OpenWebUI integration and limiter validation under issue #72 |
| Reverse proxy / Traefik | `traefik` | `traefik:v3.6.1` | `/opt/stacks/ingress/traefik/compose.yml` | `/opt/traefik/config`, `/opt/traefik/dynamic`, `/opt/traefik/certs`, `/opt/traefik/logs`, `/opt/traefik/acme` | `/traefik.yml`, `/dynamic`, `/certs`, `/logs`, `/acme` | `0.0.0.0:80`, `0.0.0.0:443`, `0.0.0.0:8443`, `127.0.0.1:18080 -> 8080` | Active documented / Persistent runtime config | Keep; routed services responded on 2026-05-21; dashboard localhost port did not respond and needs validation |

## Validated AI Model Inventory

The following model inventory was collected from live Prometheus state on 2026-05-17.

### Ollama Models

Ollama model manifests and blobs live under `/mnt/local/nvme/ai/services/ollama/models`.

| Model | Size | Status |
|---|---:|---|
| `devstral-small-2:latest` | 15 GB | Present |
| `dev-assist/glm-agent-16k:latest` | 17 GB | Present |
| `huihui_ai/glm-4.7-flash-abliterated:q4_K_S` | 17 GB | Present |
| `dev-assist/r1-architect:latest` | 17 GB | Present |
| `gpt-oss:20b` | 13 GB | Present |
| `dev-assist/mistral-general:latest` | 7.1 GB | Present |
| `dev-assist/devstral-inline:latest` | 15 GB | Present |
| `mistral-nemo:latest` | 7.1 GB | Present |
| `qwen3.5:27b` | 17 GB | Removed on 2026-05-17; replaced by llama.cpp GGUF profiles |
| `dev-assist/qwen3-workhorse:latest` | 17 GB | Removed on 2026-05-17; replaced by llama.cpp GGUF profiles |
| `hf.co/bartowski/DeepSeek-R1-Distill-Qwen-32B-GGUF:IQ4_XS` | 17 GB | Removed on 2026-05-17; replaced by llama.cpp GGUF profiles |
| `hf.co/unsloth/Qwen3-32B-GGUF:IQ4_XS` | 17 GB | Removed on 2026-05-17; replaced by llama.cpp GGUF profiles |
| `dev-assist/qwen35-workhorse:latest` | 17 GB | Removed on 2026-05-17; replaced by llama.cpp GGUF profiles |
| `dev-assist/qwen-thinking:latest` | 18 GB | Removed on 2026-05-17; replaced by llama.cpp GGUF profiles |
| `qwen3:30b-a3b-thinking-2507-q4_K_M` | 18 GB | Removed on 2026-05-17; replaced by llama.cpp GGUF profiles |

### Shared GGUF Models

Shared GGUF models live under `/mnt/local/nvme/ai/models/gguf`.

| Model Path | Notes |
|---|---|
| `/mnt/local/nvme/ai/models/gguf/gemma-4-31b-it-iq4_xs/gemma-4-31B-it-IQ4_XS.gguf` | Used by exited `gemma-192k` llama.cpp-derived container; added to `llama-swap` as `gemma-4-31b-it` on 2026-05-17 |
| `/mnt/local/nvme/ai/models/gguf/qwen3.6-35b-a3b-unsloth-ud-iq4-xs/UD-IQ4_XS/Qwen3.6-35B-A3B-UD-IQ4_XS.gguf` | Non-MTP Qwen replacement configured in `llama-swap` as `qwen3.6-35b-a3b`; 64K context, turbo3/turbo2 KV |
| `/mnt/local/nvme/ai/models/gguf/qwen3.5-9b-unsloth-ud-q4-k-xl/UD-Q4_K_XL/Qwen3.5-9B-UD-Q4_K_XL.gguf` | Non-MTP Qwen replacement configured in `llama-swap` as `qwen3.5-9b`; 128K context, turbo4/turbo3 KV |
| `/mnt/local/nvme/ai/models/gguf/qwen3.6-27b-unsloth-ud-q3-k-xl/UD-Q3_K_XL/Qwen3.6-27B-UD-Q3_K_XL.gguf` | Non-MTP Qwen replacement configured in `llama-swap` as `qwen3.6-27b`; 64K context, turbo3/turbo2 KV |
| `/mnt/local/nvme/ai/models/gguf/qwen3.6-35b-a3b-mtp-unsloth-ud-iq4-xs/UD-IQ4_XS/Qwen3.6-35B-A3B-UD-IQ4_XS.gguf` | Removed on 2026-05-17; MTP variant load validation failed against installed llama.cpp runtimes |
| `/mnt/local/nvme/ai/models/gguf/qwen3.5-9b-mtp-unsloth-ud-q4-k-xl/UD-Q4_K_XL/Qwen3.5-9B-UD-Q4_K_XL.gguf` | Removed on 2026-05-17; MTP variant load validation failed against installed llama.cpp runtimes |
| `/mnt/local/nvme/ai/models/gguf/qwen3.6-27b-mtp-unsloth-ud-q3-k-xl/UD-Q3_K_XL/Qwen3.6-27B-UD-Q3_K_XL.gguf` | Removed on 2026-05-17; MTP variant load validation failed against installed llama.cpp runtimes |
| `/mnt/local/nvme/ai/models/gguf/gemma-4-26b-a4b-it-unsloth-ud-iq4-xs/UD-IQ4_XS/gemma-4-26B-A4B-it-UD-IQ4_XS.gguf` | Installed for llama.cpp on 2026-05-17 |
| `/mnt/local/nvme/ai/models/gguf/qwen3.5-122b-a10b-unsloth-ud-iq4-xs/UD-IQ4_XS/` | Three-part GGUF set installed for llama.cpp on 2026-05-17 |
| `/mnt/local/nvme/ai/models/gguf/glm-4.6v-unsloth-ud-q3-k-xl/UD-Q3_K_XL/` | Two-part GGUF set installed for llama.cpp on 2026-05-17 |
| `/mnt/local/nvme/ai/models/gguf/glm-4.7-flash-unsloth-ud-q3-k-xl/UD-Q3_K_XL/GLM-4.7-Flash-UD-Q3_K_XL.gguf` | Installed for llama.cpp on 2026-05-17 |
| `/mnt/local/nvme/ai/models/gguf/granite-4.1-30b-unsloth-ud-q3-k-xl/UD-Q3_K_XL/granite-4.1-30b-UD-Q3_K_XL.gguf` | Installed for llama.cpp on 2026-05-17 |
| `/mnt/local/nvme/ai/models/gguf/granite-4.1-8b-unsloth-ud-q3-k-xl/UD-Q3_K_XL/granite-4.1-8b-UD-Q3_K_XL.gguf` | Installed for llama.cpp on 2026-05-17 |
| `/mnt/local/nvme/ai/models/gguf/minimax-m2-7-unsloth-ud-iq4-xs/UD-IQ4_XS/` | Four-part GGUF set |
| `/mnt/local/nvme/ai/models/gguf/nemotron-3-super-120b-a12b-unsloth-ud-q2-k-xl/UD-Q2_K_XL/` | Three-part GGUF set |
| `/mnt/local/nvme/ai/models/gguf/nemotron-3-super-120b-a12b-unsloth-ud-q3-k-xl/UD-Q3_K_XL/` | Three-part GGUF set |
| `/mnt/local/nvme/ai/models/checkpoints/v1-5-pruned-emaonly-fp16.safetensors` | ComfyUI SD1.5 checkpoint compatibility model installed 2026-05-19; `CheckpointLoaderSimple` smoke test passed |
| `/mnt/local/nvme/ai/models/diffusion_models/qwen_image_fp8_e4m3fn.safetensors` | ComfyUI image generation baseline installed 2026-05-19 |
| `/mnt/local/nvme/ai/models/diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors` | ComfyUI image editing baseline installed 2026-05-19 |
| `/mnt/local/nvme/ai/models/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors` | ComfyUI video baseline installed 2026-05-19 |
| `/mnt/local/nvme/ai/models/diffusion_models/Wan2.2-I2V-A14B-HighNoise-Q4_K_M.gguf` | ComfyUI Wan 2.2 I2V quantized high-noise GGUF installed 2026-05-19 for `ComfyUI-GGUF` loaders |
| `/mnt/local/nvme/ai/models/diffusion_models/Wan2.2-I2V-A14B-LowNoise-Q4_K_M.gguf` | ComfyUI Wan 2.2 I2V quantized low-noise GGUF installed 2026-05-19 for `ComfyUI-GGUF` loaders |
| `/mnt/local/nvme/ai/models/unet/Wan2.2-I2V-A14B-HighNoise-Q4_K_M.gguf` | ComfyUI-GGUF loader path; symlink to the high-noise GGUF file under `diffusion_models` |
| `/mnt/local/nvme/ai/models/unet/Wan2.2-I2V-A14B-LowNoise-Q4_K_M.gguf` | ComfyUI-GGUF loader path; symlink to the low-noise GGUF file under `diffusion_models` |
| `/mnt/local/nvme/ai/models/unet/ltx-2.3-22b-distilled-UD-Q4_K_S.gguf` | ComfyUI LTX 2.3 distilled Dynamic 2.0 GGUF installed 2026-05-19 from `unsloth/LTX-2.3-GGUF`; visible in `UnetLoaderGGUF` |
| `/mnt/local/nvme/ai/models/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors` | ComfyUI Qwen Image text encoder installed 2026-05-19 |
| `/mnt/local/nvme/ai/models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors` | ComfyUI Wan text encoder installed 2026-05-19 |
| `/mnt/local/nvme/ai/models/text_encoders/gemma-3-12b-it-qat-UD-Q4_K_XL.gguf` | ComfyUI LTX 2.3 Gemma GGUF installed 2026-05-19 from `unsloth/gemma-3-12b-it-qat-GGUF`; validated with `DualCLIPLoaderGGUF` |
| `/mnt/local/nvme/ai/models/text_encoders/mmproj-BF16.gguf` | ComfyUI LTX 2.3 Gemma projector installed 2026-05-19 from `unsloth/gemma-3-12b-it-qat-GGUF`; stored beside the Gemma GGUF |
| `/mnt/local/nvme/ai/models/text_encoders/ltx-2.3-22b-distilled_embeddings_connectors.safetensors` | ComfyUI LTX 2.3 distilled text connector installed 2026-05-19; validated with `DualCLIPLoaderGGUF` |
| `/mnt/local/nvme/ai/models/vae/qwen_image_vae.safetensors` | ComfyUI Qwen Image VAE installed 2026-05-19 |
| `/mnt/local/nvme/ai/models/vae/wan2.2_vae.safetensors` | ComfyUI Wan VAE installed 2026-05-19 |
| `/mnt/local/nvme/ai/models/vae/wan_2.1_vae.safetensors` | ComfyUI Wan template compatibility VAE installed 2026-05-19 |
| `/mnt/local/nvme/ai/models/vae/ltx-2.3-22b-distilled_video_vae.safetensors` | ComfyUI LTX 2.3 distilled video VAE installed 2026-05-19; validated with `VAELoaderKJ` |
| `/mnt/local/nvme/ai/models/vae/ltx-2.3-22b-distilled_audio_vae.safetensors` | ComfyUI LTX 2.3 distilled audio VAE installed 2026-05-19; validated with `VAELoaderKJ` |
| `/mnt/local/nvme/ai/models/loras/ltx-2.3-22b-distilled-lora-384.safetensors` | ComfyUI LTX 2.3 distilled LoRA installed 2026-05-19 from `Lightricks/LTX-2.3`; validated with `LoraLoaderModelOnly` |
| `/mnt/local/nvme/ai/models/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors` | ComfyUI Wan 2.2 I2V LightX2V high-noise LoRA installed 2026-05-19 |
| `/mnt/local/nvme/ai/models/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors` | ComfyUI Wan 2.2 I2V LightX2V low-noise LoRA installed 2026-05-19 |
| `/mnt/local/nvme/ai/models/upscale_models/RealESRGAN_x4plus.pth` | ComfyUI upscaler installed 2026-05-19 |
| `/mnt/local/nvme/ai/models/upscale_models/4x-UltraSharp.pth` | ComfyUI upscaler installed for trial use 2026-05-19; verify license before commercial output |
| `/mnt/local/nvme/ai/models/latent_upscale_models/ltx-2.3-spatial-upscaler-x2-1.0.safetensors` | ComfyUI LTX 2.3 spatial latent upscaler installed 2026-05-19 from `Lightricks/LTX-2.3`; validated with `LatentUpscaleModelLoader` |
| `/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/` | Qwen3-TTS 0.6B Base, 1.7B CustomVoice, and 1.7B VoiceDesign installed 2026-05-19 |
| `/mnt/local/nvme/ai/models/stt/whisper/large-v3-turbo/` | Whisper large-v3-turbo STT model installed 2026-05-19 |

### Modelfiles

Ollama Modelfiles live under `/mnt/local/ssd/ai/modelfiles`.

| File |
|---|
| `01-devstral-inline.Modelfile` |
| `02-qwen-workhorse.Modelfile` |
| `03-qwen-thinking.Modelfile` |
| `04-r1-debug.Modelfile` |
| `05-glm-agent-16k.Modelfile` |
| `06-glm-agent-32k-experimental.Modelfile` |
| `07-mistral-general.Modelfile` |
| `08-qwen35-workhorse.Modelfile` |
| `09-deepseek-r1-32b.Modelfile` |
| `deepseek-32b-stable.Modelfile` |
| `qwen3-30b-ui.Modelfile` |

## Validated Media Stack Inventory

The following media stack state is validated for Milestone 9 and reconciled into service documentation. API-level media application wiring was configured and validated on 2026-05-16; indexer configuration and end-to-end download/import tests still need validation.

| Service / Stack | Container Name | Image | Compose Path | Host Data Paths | Container Paths | Ports / Exposure | Lifecycle Classification | Recommended Action |
|---|---|---|---|---|---|---|---|---|
| Gluetun | `gluetun` | `qmcgaw/gluetun:latest` | `/opt/stacks/media/vpn/compose.yml` | `/opt/vpn/gluetun` | `/gluetun` | Publishes qBittorrent WebUI as `127.0.0.1:8080:8080` | Active documented / Persistent runtime config | Keep; preserve VPN boundary and secrets model |
| qBittorrent | `qbittorrent` | `lscr.io/linuxserver/qbittorrent:latest` | `/opt/stacks/media/vpn/compose.yml` | `/opt/torrents/config`, `/opt/torrents/downloads` | `/config`, `/downloads` | `network_mode: service:gluetun`; WebUI localhost-only through Gluetun | Active documented / Local staging disposable | Keep; version `v5.1.4`, default save path `/downloads`, and categories `radarr`, `sonarr`, `mam`, `manual` validated |
| Prowlarr | `prowlarr` | `lscr.io/linuxserver/prowlarr:latest` | `/opt/stacks/media/vpn/compose.yml` | `/opt/arr/prowlarr` | `/config` | `0.0.0.0:9696` temporary broad exposure | Active documented / Persistent runtime config | Keep; reduce exposure in future ingress/security pass |
| Radarr | `radarr` | `lscr.io/linuxserver/radarr:latest` | `/opt/stacks/media/vpn/compose.yml` | `/opt/arr/radarr`, `/opt/torrents/downloads`, `/mnt/atlas/managed-media/movies` | `/config`, `/downloads`, `/movies` | `0.0.0.0:7878` temporary broad exposure | Active documented / Persistent runtime config with Atlas authoritative library | Keep; `SKIP_CHOWN=true`, root folder `/movies`, and qBittorrent category `radarr` validated |
| Sonarr | `sonarr` | `lscr.io/linuxserver/sonarr:latest` | `/opt/stacks/media/vpn/compose.yml` | `/opt/arr/sonarr`, `/opt/torrents/downloads`, `/mnt/atlas/managed-media/tv` | `/config`, `/downloads`, `/tv` | `0.0.0.0:8989` temporary broad exposure | Active documented / Persistent runtime config with Atlas authoritative library | Keep; `SKIP_CHOWN=true`, root folder `/tv`, and qBittorrent category `sonarr` validated |

## Validated Atlas Media Mounts

| Atlas Export | Prometheus Mount | Status | Notes |
|---|---|---|---|
| `192.168.60.102:/mnt/user/managed-media` | `/mnt/atlas/managed-media` | Active | Authoritative managed media share. |
| `192.168.60.102:/mnt/user/shared-media` | `/mnt/atlas/shared-media` | Active | Authoritative shared media share. |
| `/mnt/atlas/downloads` | Not applicable | Not active | Not an active Atlas export; downloads remain local on Prometheus. |

## Requested Inventory Items Needing Validation

The following items are explicitly requested for this inventory, but current repository documentation does not prove their deployed state, compose paths, images, ports, or data paths.

| Service / Stack | Container Name | Image | Compose Path | Host Data Paths | Container Paths | Ports / Exposure | Lifecycle Classification | Recommended Action |
|---|---|---|---|---|---|---|---|---|
| Homelable | `/opt/homelable/docker-compose.yml` | `homelable-backend-1`, `homelable-frontend-1`, `homelable-mcp-1` built from source | `/opt/homelable/docker-compose.yml` | `homelable_backend_data` Docker volume (SQLite) | `/app/data` (backend) | `0.0.0.0:3000 -> 80/tcp`, `0.0.0.0:8001 -> 8001/tcp`; no Traefik route | Active documented / needs route remediation | Route through Traefik and rotate default secrets; tracked by service doc |
| SearXNG | See active documented inventory | `searxng/searxng:latest` | `/opt/stacks/ai/searxng/compose.yml` | `/mnt/local/ssd/ai/services/searxng/searxng`; anonymous cache volume | `/etc/searxng`, `/var/cache/searxng` | Traefik route `searxng.home.arpa` | Active documented | Tracked under issue #72; OpenWebUI web search still disabled |
| SearXNG Redis | See active documented inventory | `redis:7-alpine` | `/opt/stacks/ai/searxng/compose.yml` | Anonymous Docker volume | `/data` | Docker networks only | Active documented | Dedicated to SearXNG |
| Gluetun | See validated media stack inventory | `qmcgaw/gluetun:latest` | `/opt/stacks/media/vpn/compose.yml` | `/opt/vpn/gluetun` | `/gluetun` | `127.0.0.1:8080:8080` for qBittorrent WebUI through Gluetun | Active documented | Original requested row reconciled above |
| qBittorrent | See validated media stack inventory | `lscr.io/linuxserver/qbittorrent:latest` | `/opt/stacks/media/vpn/compose.yml` | `/opt/torrents/config`, `/opt/torrents/downloads` | `/config`, `/downloads` | Localhost-only through Gluetun | Active documented | Original requested row reconciled above; download transfer test still needs validation |
| Radarr | See validated media stack inventory | `lscr.io/linuxserver/radarr:latest` | `/opt/stacks/media/vpn/compose.yml` | `/opt/arr/radarr`, Atlas movies, local downloads | `/config`, `/movies`, `/downloads` | `0.0.0.0:7878` temporary broad exposure | Active documented | Original requested row reconciled above; import test still needs validation |
| Sonarr | See validated media stack inventory | `lscr.io/linuxserver/sonarr:latest` | `/opt/stacks/media/vpn/compose.yml` | `/opt/arr/sonarr`, Atlas TV, local downloads | `/config`, `/tv`, `/downloads` | `0.0.0.0:8989` temporary broad exposure | Active documented | Original requested row reconciled above; import test still needs validation |
| Prowlarr | See validated media stack inventory | `lscr.io/linuxserver/prowlarr:latest` | `/opt/stacks/media/vpn/compose.yml` | `/opt/arr/prowlarr` | `/config` | `0.0.0.0:9696` temporary broad exposure | Active documented | Original requested row reconciled above; Radarr/Sonarr app links validated; indexers still need validation |
| Portainer | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Active needs validation | Confirm MGMT-only or localhost-only access before deployment/docs closeout |
| Jellyfin | Needs validation | Needs validation | Needs validation | Target mount `/mnt/atlas/managed-media:/media:ro` needs validation | `/media` target needs validation | Needs validation | Migration candidate / Needs validation | Do not mark deployed; confirm compose source, config path, library paths, and network exposure before deployment |

## Questionable / Exited Containers

These items are named in the issue scope but are not documented elsewhere in the repository.

| Service / Stack | Container Name | Image | Compose Path | Host Data Paths | Container Paths | Ports / Exposure | Lifecycle Classification | Recommended Action |
|---|---|---|---|---|---|---|---|---|
| Unknown | `anemoi` | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Questionable / exited needs validation | Inspect live Docker state; do not delete until owner and data paths are identified |
| Unknown | `gemma-192k` | Needs validation | Needs validation | Needs validation | Needs validation | Needs validation | Questionable / exited needs validation | Inspect live Docker state; confirm whether this is model/runtime residue |
| Docker volumes | Anonymous Docker volumes | Needs validation | Not applicable | Needs validation | Needs validation | Not applicable | Cleanup candidate / Needs validation | Run read-only Docker volume inventory before pruning; do not delete from docs alone |

## Required Live Inventory Commands

Run these only when explicitly approved on Prometheus.

```bash
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
docker compose ls
docker volume ls
docker volume inspect $(docker volume ls -q)
find /opt -maxdepth 3 -name 'docker-compose.yml' -o -name 'compose.yml'
find ~/stacks -maxdepth 4 -name 'docker-compose.yml' -o -name 'compose.yml'
find /mnt/local -maxdepth 5 -name 'docker-compose.yml' -o -name 'compose.yml'
```

## Stop Points

- Do not delete containers from this inventory alone.
- Do not prune anonymous volumes until ownership is validated.
- Do not move stacks between `/opt`, `~/stacks`, and `/mnt/local` until compose files and data paths are mapped.
- Do not expose services while documenting inventory.
- Do not convert `Needs validation` rows into facts without repository evidence.
