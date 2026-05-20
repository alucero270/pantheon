---
type: procedure
risk_level: medium
last_tested: 2026-05-19
---

# ComfyUI Creative Production Workflow

## Purpose

This procedure is a beginner entrypoint for using [[systems/prometheus/services/comfyui]] on [[systems/prometheus]] to produce creative assets:

- images
- video
- audio
- text-to-speech (TTS)
- speech-tdo-text (STT)

It starts with the basic ComfyUI mental model, then walks from a new project to finished output.

This is a production workflow guide, not an architecture decision. Prometheus remains disposable compute; final authoritative creative assets should be copied to the approved long-term storage location when a project is complete.

## What Is ComfyUI?

ComfyUI is a node-based interface for AI media generation.

Instead of filling out one long form, you build a graph:

```text
input nodes -> model/processing nodes -> output nodes
```

Each box is a node. Lines between boxes pass data.

Common data types:

| Type | Meaning |
|---|---|
| `MODEL` | The neural network used for generation |
| `CLIP` / text encoder | Turns text prompts into conditioning the model can use |
| `VAE` | Converts between latent images and visible images |
| `LATENT` | Compressed image/video data used during sampling |
| `IMAGE` | Normal image data |
| `AUDIO` | Audio waveform data |
| `CONDITIONING` | Positive or negative prompt information |

Common node categories:

| Node kind | What it does |
|---|---|
| Loader nodes | Load checkpoints, diffusion models, VAEs, text encoders, upscalers, audio models, or input files |
| Prompt nodes | Encode text prompts for the model |
| Latent nodes | Create empty image/video/audio latent space |
| Sampler nodes | Generate media by denoising latent space |
| Decode nodes | Convert latent output into image, video, or audio |
| Save nodes | Write final files to disk |

## Access

Open ComfyUI from a client that can resolve the homelab DNS route:

```text
https://comfy.home.arpa
```

Prometheus-side validation:

```bash
curl -k --resolve comfy.home.arpa:443:127.0.0.1 https://comfy.home.arpa/
```

Expected:

- HTTP `200`
- ComfyUI web UI loads

## Storage Model

Use the documented Prometheus paths.

| Purpose | Host path | Container path |
|---|---|---|
| ComfyUI runtime | `/mnt/local/nvme/ai/services/comfy-mnt` | `/comfy/mnt` |
| Shared models | `/mnt/local/nvme/ai/models` | `/comfy/shared-models` |
| Output files | `/mnt/local/ssd/ai/outputs/comfy` | `/comfy/mnt/output` |
| ComfyUI app output path | `/mnt/local/nvme/ai/services/comfy-mnt/ComfyUI/output` | symlink to `/comfy/mnt/output` |

Do not mount individual subdirectories into `/comfy/mnt`. The container image requires `/comfy/mnt` to be one bind mount owned by UID/GID `1024:1024`.

## Installed Production Baseline

The following baseline was installed and validated on 2026-05-19.

| Capability | Model / file | Path |
|---|---|---|
| SD1.5 checkpoint workflow compatibility | `v1-5-pruned-emaonly-fp16.safetensors` | `/mnt/local/nvme/ai/models/checkpoints` |
| Qwen image generation | `qwen_image_fp8_e4m3fn.safetensors` | `/mnt/local/nvme/ai/models/diffusion_models` |
| Qwen image editing | `qwen_image_edit_2509_fp8_e4m3fn.safetensors` | `/mnt/local/nvme/ai/models/diffusion_models` |
| Qwen image text encoder | `qwen_2.5_vl_7b_fp8_scaled.safetensors` | `/mnt/local/nvme/ai/models/text_encoders` |
| Qwen image VAE | `qwen_image_vae.safetensors` | `/mnt/local/nvme/ai/models/vae` |
| Wan video | `wan2.2_ti2v_5B_fp16.safetensors` | `/mnt/local/nvme/ai/models/diffusion_models` |
| Wan I2V quantized video | `Wan2.2-I2V-A14B-HighNoise-Q4_K_M.gguf`, `Wan2.2-I2V-A14B-LowNoise-Q4_K_M.gguf` | `/mnt/local/nvme/ai/models/unet` |
| LTX 2.3 distilled video | `ltx-2.3-22b-distilled-UD-Q4_K_S.gguf` | `/mnt/local/nvme/ai/models/unet` |
| LTX 2.3 text encoder, projector, and connector | `gemma-3-12b-it-qat-UD-Q4_K_XL.gguf`, `mmproj-BF16.gguf`, `ltx-2.3-22b-distilled_embeddings_connectors.safetensors` | `/mnt/local/nvme/ai/models/text_encoders` |
| LTX 2.3 distilled VAEs | `ltx-2.3-22b-distilled_video_vae.safetensors`, `ltx-2.3-22b-distilled_audio_vae.safetensors` | `/mnt/local/nvme/ai/models/vae` |
| LTX 2.3 distilled LoRA | `ltx-2.3-22b-distilled-lora-384.safetensors` | `/mnt/local/nvme/ai/models/loras` |
| LTX 2.3 latent upscaler | `ltx-2.3-spatial-upscaler-x2-1.0.safetensors` | `/mnt/local/nvme/ai/models/latent_upscale_models` |
| Wan text encoder | `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | `/mnt/local/nvme/ai/models/text_encoders` |
| Wan VAE | `wan2.2_vae.safetensors`, `wan_2.1_vae.safetensors` | `/mnt/local/nvme/ai/models/vae` |
| Wan I2V LightX2V LoRAs | `wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors`, `wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors` | `/mnt/local/nvme/ai/models/loras` |
| Upscaling | `RealESRGAN_x4plus.pth` | `/mnt/local/nvme/ai/models/upscale_models` |
| Upscaling trial model | `4x-UltraSharp.pth` | `/mnt/local/nvme/ai/models/upscale_models` |
| TTS / voice | Qwen3-TTS 0.6B Base, 1.7B CustomVoice, 1.7B VoiceDesign | `/mnt/local/nvme/ai/models/TTS/Qwen3-TTS` |
| STT | Whisper large-v3-turbo | `/mnt/local/nvme/ai/models/stt/whisper/large-v3-turbo` |

`4x-UltraSharp.pth` is installed for trial use. Verify license suitability before using it for commercial deliverables.

## Installing Models

Install ComfyUI models into the shared model root:

```bash
/mnt/local/nvme/ai/models
```

Use these category folders:

```text
/mnt/local/nvme/ai/models/checkpoints
/mnt/local/nvme/ai/models/diffusion_models
/mnt/local/nvme/ai/models/unet
/mnt/local/nvme/ai/models/text_encoders
/mnt/local/nvme/ai/models/vae
/mnt/local/nvme/ai/models/loras
/mnt/local/nvme/ai/models/controlnet
/mnt/local/nvme/ai/models/clip_vision
/mnt/local/nvme/ai/models/style_models
/mnt/local/nvme/ai/models/upscale_models
/mnt/local/nvme/ai/models/latent_upscale_models
/mnt/local/nvme/ai/models/audio_encoders
/mnt/local/nvme/ai/models/TTS
/mnt/local/nvme/ai/models/stt
```

### Create Folders

```bash
mkdir -p \
  /mnt/local/nvme/ai/models/checkpoints \
  /mnt/local/nvme/ai/models/diffusion_models \
  /mnt/local/nvme/ai/models/unet \
  /mnt/local/nvme/ai/models/text_encoders \
  /mnt/local/nvme/ai/models/vae \
  /mnt/local/nvme/ai/models/loras \
  /mnt/local/nvme/ai/models/controlnet \
  /mnt/local/nvme/ai/models/clip_vision \
  /mnt/local/nvme/ai/models/style_models \
  /mnt/local/nvme/ai/models/upscale_models \
  /mnt/local/nvme/ai/models/latent_upscale_models \
  /mnt/local/nvme/ai/models/audio_encoders \
  /mnt/local/nvme/ai/models/TTS \
  /mnt/local/nvme/ai/models/stt
```

### Make ComfyUI See the Shared Model Root

ComfyUI is configured through:

```bash
/mnt/local/nvme/ai/services/comfy-mnt/ComfyUI/extra_model_paths.yaml
```

Expected content:

```yaml
comfyui_shared:
  base_path: /comfy/shared-models
  is_default: true
  checkpoints: checkpoints
  text_encoders: text_encoders
  clip: text_encoders
  clip_vision: clip_vision
  configs: configs
  controlnet: controlnet
  diffusion_models: diffusion_models
  unet: unet
  embeddings: embeddings
  loras: loras
  upscale_models: upscale_models
  latent_upscale_models: latent_upscale_models
  vae: vae
  style_models: style_models
  audio_encoders: audio_encoders
  model_patches: model_patches
  TTS: TTS
  stt: stt
```

Restart ComfyUI after model or path changes:

```bash
docker restart comfy
```

## New Project To Finished Product

Use this repeatable project flow for any asset type.

### 1. Define The Deliverable

Write down:

| Field | Example |
|---|---|
| Campaign | Local service launch |
| Deliverable | Square Instagram ad |
| Size | 1080x1080 |
| Brand colors | blue, white, black |
| Text required | "Book Today" |
| Output format | PNG |
| Source assets | logo, product photo, voice reference |

### 2. Create A Project Folder

Use SSD output space for generated work:

```bash
mkdir -p /mnt/local/ssd/ai/outputs/comfy/projects/example-campaign/{inputs,work,final}
```

Recommended layout:

```text
/mnt/local/ssd/ai/outputs/comfy/projects/example-campaign/
  inputs/
  work/
  final/
```

Put uploaded logos, product photos, reference images, scripts, and voice samples in `inputs`.

### 3. Pick The Workflow Type

| Goal | Start with |
|---|---|
| Simple legacy image workflow | SD1.5 checkpoint workflow |
| Better text in ads/flyers | Qwen Image workflow |
| Edit a product/photo/flyer | Qwen Image Edit workflow |
| Short clip or commercial shot | Wan video workflow |
| Narration or voice clone | Qwen3-TTS workflow |
| Transcription or captions | Whisper STT workflow |

### 4. Build Or Load A Workflow

In the ComfyUI web UI:

1. Open `https://comfy.home.arpa`.
2. Load an existing workflow JSON, or create nodes manually.
3. Select the correct model files in loader nodes.
4. Set prompt text, dimensions, steps, and output prefix.
5. Click `Queue Prompt`.
6. Review output under `/mnt/local/ssd/ai/outputs/comfy`.
7. Move final selected files into the project `final` folder.

### 5. Save The Workflow

After a useful result:

1. Save the workflow JSON from ComfyUI.
2. Store it with the project.

Suggested path:

```text
/mnt/local/ssd/ai/outputs/comfy/projects/example-campaign/work/workflow.json
```

Do not rely only on browser state.

## Image Workflow

### Option A: SD1.5 Beginner Workflow

Use this for old workflows that use `CheckpointLoaderSimple`.

Required model:

```text
/mnt/local/nvme/ai/models/checkpoints/v1-5-pruned-emaonly-fp16.safetensors
```

Minimum node chain:

```text
CheckpointLoaderSimple
  -> CLIPTextEncode (positive)
  -> CLIPTextEncode (negative)
  -> EmptyLatentImage
  -> KSampler
  -> VAEDecode
  -> SaveImage
```

Node descriptions:

| Node | Beginner meaning |
|---|---|
| `CheckpointLoaderSimple` | Loads one complete SD checkpoint containing model, text encoder, and VAE |
| `CLIPTextEncode` positive | What the image should contain |
| `CLIPTextEncode` negative | What the image should avoid |
| `EmptyLatentImage` | Canvas size and batch size |
| `KSampler` | The generation engine |
| `VAEDecode` | Converts generated latent data into an image |
| `SaveImage` | Writes PNG output |

Recommended beginner settings:

| Setting | Value |
|---|---|
| Width | `512` |
| Height | `512` |
| Steps | `20` |
| Sampler | `euler` or `dpmpp_2m` |
| Scheduler | `normal` or `karras` |
| CFG | `6` to `8` |

Validation already performed:

```text
CheckpointLoaderSimple -> KSampler -> SaveImage
```

Output:

```text
/mnt/local/ssd/ai/outputs/comfy/codex_smoke/sd15_checkpoint_smoke_00001_.png
```

### Option B: Qwen Image For Ads And Flyers

Use this for better text rendering and commercial-style image/flyer generation.

Required models:

```text
/mnt/local/nvme/ai/models/diffusion_models/qwen_image_fp8_e4m3fn.safetensors
/mnt/local/nvme/ai/models/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors
/mnt/local/nvme/ai/models/vae/qwen_image_vae.safetensors
```

Typical node families:

```text
UNETLoader
CLIPLoader or text encoder loader
VAELoader
Qwen-compatible prompt/text encode nodes
EmptyQwenImageLayeredLatentImage or compatible latent node
Sampler
VAE decode
SaveImage
```

Exact node names can change with ComfyUI versions and installed custom nodes. If a downloaded official workflow fails because a node is missing, install the required custom node through ComfyUI Manager, then restart `comfy`.

Prompt style:

```text
A polished square advertisement for a local premium detailing service.
Clean white background, blue accent color, modern typography.
Text: "Book Today"
Include space for a logo in the top left.
High contrast, professional, ready for social media.
```

Workflow tips:

- Keep text short.
- Generate several variants.
- Use upscaling after selecting the best draft.
- Save the workflow JSON with the project.

## Image Editing Workflow

Use Qwen Image Edit when you already have a product image, flyer draft, or reference image.

Required models:

```text
/mnt/local/nvme/ai/models/diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors
/mnt/local/nvme/ai/models/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors
/mnt/local/nvme/ai/models/vae/qwen_image_vae.safetensors
```

Typical node families:

```text
LoadImage
UNETLoader
text encoder loader
VAELoader
Qwen image edit conditioning nodes
Sampler
VAE decode
SaveImage
```

Beginner edit prompt examples:

```text
Replace the background with a clean studio background. Keep the product unchanged.
```

```text
Turn this into a polished flyer. Add the text "Grand Opening" and leave space at the bottom for contact details.
```

Project practice:

- Keep source files in `inputs`.
- Save drafts in `work`.
- Save approved exports in `final`.

## Upscaling Workflow

Use after generating or editing an image.

Installed upscalers:

```text
/mnt/local/nvme/ai/models/upscale_models/RealESRGAN_x4plus.pth
/mnt/local/nvme/ai/models/upscale_models/4x-UltraSharp.pth
```

Minimum node chain:

```text
LoadImage
UpscaleModelLoader
ImageUpscaleWithModel
SaveImage
```

Use `RealESRGAN_x4plus.pth` as the default. Use `4x-UltraSharp.pth` for experiments, but verify license suitability before commercial work.

## Video Workflow

Use video workflows for social clips, product motion, b-roll, and commercial drafts.

Installed baseline:

```text
/mnt/local/nvme/ai/models/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors
/mnt/local/nvme/ai/models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors
/mnt/local/nvme/ai/models/vae/wan2.2_vae.safetensors
```

Beginner target:

| Setting | Starting value |
|---|---|
| Duration | 3 to 5 seconds |
| Resolution | 480p or lower at first |
| FPS | 12 to 16 |
| Batch | 1 |

Typical node families:

```text
UNETLoader or UnetLoaderGGUF
text encoder loader
VAELoader
video latent node
video sampler
video decode
SaveVideo
```

Text-to-video prompt example:

```text
A short commercial shot of a clean product on a white studio table.
Slow camera push-in, soft light, professional advertisement style.
```

Image-to-video prompt example:

```text
Animate this product photo with a slow cinematic push-in.
Keep the product shape and branding stable.
```

Practical warnings:

- Video generation uses much more VRAM and time than image generation.
- Start small before increasing resolution or frame count.
- Keep prompts simple until the workflow is validated.
- If ComfyUI runs out of VRAM, lower resolution, frame count, or model precision before changing infrastructure.
- If using the Wan 2.2 I2V Q4_K_M GGUF files, replace normal FP8 `UNETLoader` nodes with `UnetLoaderGGUF` or `UnetLoaderGGUFAdvanced`.
- Keep GGUF UNET files visible under `/mnt/local/nvme/ai/models/unet`. The standard `diffusion_models` category is validated for `.safetensors` and `.sft` workflows, while `ComfyUI-GGUF` exposes `.gguf` files through the `unet` category.
- When patching exported templates, do not add `properties.models` download metadata with `directory: unet` for GGUF nodes. ComfyUI-GGUF registers its loader folder internally as `unet_gguf`, and the frontend missing-model helper may reject `unet` metadata even when the loader itself can see the file.
- The Wan 2.2 LightX2V 4-step LoRAs were partially validated against the Q4_K_M GGUF path on 2026-05-19. The original dual-LoRA graph completed and produced a usable sample, but it emitted many LoRA tensor shape warnings. Cleaner API smoke tests completed with one LoRA enabled at a time:
  - High-noise LoRA only: `wan22_high_lora_codex_00001_.mp4`, 640x640, 81 frames, 16 fps, 5.06 seconds, completed in about 142 seconds.
  - Low-noise LoRA only: `wan22_low_lora_codex_00001_.mp4`, 640x640, 81 frames, 16 fps, 5.06 seconds, completed in about 160 seconds.
- For Wan GGUF LoRA testing, prefer a single `LoraLoaderModelOnly` on either the high-noise stage or low-noise stage before re-enabling both LoRAs together.
- LTX 2.3 distilled `UD-Q4_K_S` GGUF + LoRA validation succeeded on 2026-05-19 after ComfyUI was reset to clean upstream `0.21.1` and custom node dependencies were reinstalled. The active validated Unsloth-derived path uses `DualCLIPLoaderGGUF`, `UnetLoaderGGUF`, `VAELoaderKJ`, `LoraLoaderModelOnly`, `LTXVEmptyLatentAudio`, `LTXVLatentUpsampler`, and `SaveVideo`.

### LTX 2.3 Unsloth GGUF + LoRA Validated Workflow

Workflow artifacts:

```text
systems/prometheus/procedures/workflows/comfyui/unsloth_ltx23_flowers_embedded_ui.json
systems/prometheus/procedures/workflows/comfyui/unsloth_ltx23_flowers_embedded_api.json
systems/prometheus/procedures/workflows/comfyui/unsloth_ltx23_flowers_udq4ks_ui.json
systems/prometheus/procedures/workflows/comfyui/unsloth_ltx23_flowers_udq4ks_api.json
systems/prometheus/procedures/workflows/comfyui/unsloth_ltx23_flowers_udq4ks_smoke_api.json
systems/prometheus/procedures/workflows/comfyui/unsloth_ltx23_high_action_max_udq4ks_api.json
```

The embedded Unsloth workflow was extracted from `C:\Users\Alex Lucero\Downloads\unsloth_flowers.mp4`. The embedded workflow referenced the dev `Q4_K_M` model family; the validated Pantheon variant switches the graph to the installed distilled `UD-Q4_K_S` model family.

Validated model set on 2026-05-19:

| Field | Value |
|---|---|
| ComfyUI version | `0.21.1`, clean upstream source |
| Model loader | `UnetLoaderGGUF` with `ltx-2.3-22b-distilled-UD-Q4_K_S.gguf` |
| Text loader | `DualCLIPLoaderGGUF` with `gemma-3-12b-it-qat-UD-Q4_K_XL.gguf` and `ltx-2.3-22b-distilled_embeddings_connectors.safetensors` |
| Projector file | `mmproj-BF16.gguf`, installed beside the Gemma GGUF |
| VAE loaders | `VAELoaderKJ` with `ltx-2.3-22b-distilled_video_vae.safetensors` and `ltx-2.3-22b-distilled_audio_vae.safetensors` |
| LoRA loader | `LoraLoaderModelOnly` with `ltx-2.3-22b-distilled-lora-384.safetensors` |
| Latent upscaler | `LatentUpscaleModelLoader` with `ltx-2.3-spatial-upscaler-x2-1.0.safetensors` |
| Video/audio assembly | `CreateVideo` and `SaveVideo` |
| Status | Validated |

Validation results:

| Prompt id | Workflow | Settings | Output | Result |
|---|---|---|---|---|
| `641147e2-774f-4a97-9750-64c31ec6568c` | `unsloth_ltx23_flowers_udq4ks_smoke_api.json` | 640x360 source, 17 frames, 8 fps, 4 first-pass steps | `codex_smoke/unsloth_ltx23_udq4ks_smoke_00001_.mp4` | Completed |
| `9f8baafc-4811-4470-99d3-2f7ede7a471e` | `unsloth_ltx23_high_action_max_udq4ks_api.json` | 1280x720 source, 121 frames, 24 fps, 20 first-pass steps, LoRA refinement, audio path | `codex_max/ltx23_high_action_udq4ks_1280x720_121f_24fps_00001_.mp4` | Completed |

The max-render output probed locally as H.264 video plus AAC audio: 1280x704, 121 frames, 24 fps, 5.041667 seconds, 3,053,559 bytes. The height aligned from requested 720 to 704 during the LTX video path.

Frame length has not yet been tested beyond 121 frames. Candidate next steps should keep the LTX-style `8n + 1` frame pattern: 145, 169, 193, 217, or 241 frames. Restart `comfy` before longer tests to clear held VRAM. Longer outputs remain `Needs validation` under GitHub issue #109.

Earlier KJ-node smoke artifact:

```text
systems/prometheus/procedures/workflows/comfyui/ltx23_gguf_kj_lora_clean_api.json
```

This path completed prompt `b5590bb8-9d92-4f6d-a953-c671045806a1` and wrote `codex_smoke/ltx23_gguf_kj_lora_clean_00001_.mp4`, but it depended on alternate files that were removed from the active model folders after the Unsloth GGUF path was selected: `gemma_3_12B_it_fp4_mixed.safetensors`, `ltx-2.3-22b-distilled-lora-384-1.1.safetensors`, and `taeltx2_3.safetensors`.

### LTX 2 Image-To-Video Template Candidate

Candidate workflow artifact:

```text
systems/prometheus/procedures/workflows/comfyui/video_ltx2_i2v_distilled.json
```

This artifact is an LTX 2.0 distilled image-to-video template, not the validated LTX 2.3 GGUF + LoRA workflow. It is useful as a graph shape for future image-to-video validation because it uses LTX-specific nodes rather than the prior Wan 2.2 path.

Observed template characteristics:

| Area | Template evidence | LTX 2.3 validation implication |
|---|---|---|
| Base model | `CheckpointLoaderSimple` with `ltx-2-19b-distilled.safetensors` | Needs adaptation for installed `ltx-2.3-22b-distilled-UD-Q4_K_S.gguf` under `/mnt/local/nvme/ai/models/unet` |
| Text encoder | `LTXAVTextEncoderLoader` and `gemma_3_12B_it_fp4_mixed.safetensors` | Historical template path only; the active validated LTX 2.3 Unsloth path uses `DualCLIPLoaderGGUF` with `gemma-3-12b-it-qat-UD-Q4_K_XL.gguf` and `ltx-2.3-22b-distilled_embeddings_connectors.safetensors` |
| VAE/audio | LTX video/audio VAE nodes are present in the subgraph | Needs validation against installed LTX 2.3 VAE files |
| LoRA | `LoraLoaderModelOnly` appears in the subgraph | Validate one LTX-compatible LoRA at a time before combining LoRAs |
| Image-to-video path | `LoadImage`, resize, LTXV preprocessing, latent generation, sampling, decode, `SaveVideo` | Preferred starting point for LTX 2.3 I2V testing |

Validation rules:

- Keep the first LTX 2.3 test small: 480p or lower, short frame count, one LoRA, batch 1.
- Record the exact loader node, model filename, LoRA filename, output filename, frame count, resolution, runtime, and any warnings.
- If LoRA tensor-shape warnings appear, fall back to no LoRA and then test a single known LTX-compatible LoRA.
- Status: Needs validation for image-to-video adaptation; tracked by GitHub issue #109.

## Audio Workflow

Audio in ComfyUI can mean generated audio, loaded audio, voiceover, or audio attached to video.

Validated runtime fix:

- `torch`: `2.12.0+cu130`
- `torchaudio`: `2.11.0+cu130`

If audio nodes fail to import, check:

```bash
docker logs --tail=200 comfy | grep -Ei "torchaudio|audio|import failed|traceback"
```

Audio output nodes currently visible include:

```text
SaveAudio
SaveAudioMP3
SaveAudioOpus
PreviewAudio
```

General audio node chain:

```text
LoadAudio or generated audio node
audio processing node
SaveAudio or SaveAudioMP3
```

Use the project folder layout:

```text
projects/example-campaign/inputs/voice-reference.wav
projects/example-campaign/work/narration-draft.wav
projects/example-campaign/final/narration-final.wav
```

## TTS Workflow

TTS means text-to-speech: text in, voice audio out.

Installed models:

```text
/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-0.6B-Base
/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice
/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-VoiceDesign
```

Suggested use:

| Model | Use |
|---|---|
| 0.6B Base | Fast first tests and simple cloning |
| 1.7B CustomVoice | Better reusable custom voice work |
| 1.7B VoiceDesign | Voice design from description |

Typical node families:

```text
TTS model loader
text input
optional reference audio input
TTS generation node
SaveAudio or SaveAudioMP3
```

Beginner narration script:

```text
Book your appointment today and give your vehicle the clean finish it deserves.
```

Voice clone caution:

- Use only voices you own or have permission to clone.
- Keep consent records with the project.
- Do not treat voice cloning as approved for public/commercial output without rights validation.

Status:

- Models are installed.
- ComfyUI audio imports were repaired.
- End-to-end Qwen3-TTS workflow still needs workflow/custom-node validation.

## STT Workflow

STT means speech-to-text: audio in, transcript out.

Installed model:

```text
/mnt/local/nvme/ai/models/stt/whisper/large-v3-turbo
```

Use cases:

- turn voiceover into captions
- transcribe meeting/audio notes
- create subtitle text for commercials
- extract script timing from a reference video

Typical node families:

```text
LoadAudio
Whisper / STT model loader
transcription node
text output or file save node
```

Caption workflow:

1. Put source audio in the project `inputs` folder.
2. Load it in ComfyUI.
3. Run Whisper transcription.
4. Save transcript to the project `work` folder.
5. Edit transcript manually.
6. Use final transcript for captions, OpenWebUI prompts, or video assembly.

Status:

- Whisper model is installed.
- ComfyUI audio imports were repaired.
- End-to-end STT workflow still needs workflow/custom-node validation.

## Finished Product Checklist

Before calling a project done:

- workflow JSON is saved
- source assets are stored under `inputs`
- drafts are under `work`
- final exports are under `final`
- prompts and model names are documented
- commercial license posture is known for every model used
- generated output was reviewed manually
- final files are copied to authoritative storage if needed

## Validation Commands

Run from Prometheus.

### Service

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "^comfy\b|NAMES"
```

Expected:

- `comfy` is up
- only container port `8188/tcp` is shown
- no host port is published

### Route

```bash
curl -k -fsS -o /dev/null -w "comfy route HTTP %{http_code}\n" \
  --resolve comfy.home.arpa:443:127.0.0.1 \
  https://comfy.home.arpa/
```

Expected:

```text
comfy route HTTP 200
```

### GPU And Runtime

```bash
docker exec comfy sh -lc 'wget -qO- http://127.0.0.1:8188/system_stats'
```

Expected:

- ComfyUI version is present
- PyTorch version is present
- RTX 4000 Ada is present

### Model Visibility

```bash
docker exec comfy sh -lc 'wget -qO /tmp/object_info.json http://127.0.0.1:8188/object_info && python3 - << "PY"
import json
s=json.dumps(json.load(open("/tmp/object_info.json")))
for n in [
    "v1-5-pruned-emaonly-fp16.safetensors",
    "qwen_image_fp8_e4m3fn.safetensors",
    "qwen_image_edit_2509_fp8_e4m3fn.safetensors",
    "qwen_2.5_vl_7b_fp8_scaled.safetensors",
    "qwen_image_vae.safetensors",
    "wan2.2_ti2v_5B_fp16.safetensors",
    "wan2.2_vae.safetensors",
    "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
    "RealESRGAN_x4plus.pth",
    "4x-UltraSharp.pth",
]:
    print(("FOUND" if n in s else "MISSING"), n)
PY'
```

Expected:

- all listed files print `FOUND`

### Output Path

```bash
docker exec comfy sh -lc 'ls -ld /comfy/mnt/ComfyUI/output /comfy/mnt/output; readlink -f /comfy/mnt/ComfyUI/output'
```

Expected:

```text
/comfy/mnt/ComfyUI/output -> ../output
/comfy/mnt/output
```

## Troubleshooting

### `Value not in list: ckpt_name ... not in []`

Cause:

- The workflow uses `CheckpointLoaderSimple`, but no checkpoint is installed or visible in `checkpoints`.

Fix:

1. Install the checkpoint under:

   ```text
   /mnt/local/nvme/ai/models/checkpoints
   ```

2. Restart ComfyUI:

   ```bash
   docker restart comfy
   ```

3. Refresh the browser and select the checkpoint again.

### Qwen Or Wan Model Not In Dropdown

Cause:

- The workflow uses the wrong loader type.

Fix:

- Checkpoint workflows use `CheckpointLoaderSimple`.
- Qwen/Wan split models use loaders for diffusion model, text encoder, and VAE.

### Output Does Not Appear On SSD

Check:

```bash
docker exec comfy sh -lc 'readlink -f /comfy/mnt/ComfyUI/output'
```

Expected:

```text
/comfy/mnt/output
```

Host path:

```text
/mnt/local/ssd/ai/outputs/comfy
```

### Audio Nodes Fail

Check:

```bash
docker logs --tail=200 comfy | grep -Ei "torchaudio|audio|import failed|traceback"
```

Known validated fix on 2026-05-19:

```bash
docker exec comfy sh -lc '/comfy/mnt/venv/bin/python3 -m pip install --force-reinstall --no-deps --index-url https://download.pytorch.org/whl/cu130 torchaudio==2.11.0+cu130'
docker restart comfy
```

Use this only if PyTorch is still `2.12.0+cu130`.

### Browser Dropdown Looks Stale

Fix:

1. Restart ComfyUI.
2. Hard refresh the browser.
3. Reopen the loader node dropdown.

## Stop Points

- Do not loosen Traefik exposure from this procedure.
- Do not change DNS from this procedure.
- Do not use voice cloning without rights/consent validation.
- Do not treat trial models as commercially approved without license review.
- Do not assume generated output is factual or rights-clean without manual review.

## Related Docs

- [[systems/prometheus/services/comfyui]]
- [[systems/prometheus/inventory]]
- [[systems/prometheus/procedures/ai-stack-initialization]]
- [[systems/prometheus/procedures/reverse-proxy-validation]]
- [[decisions/ADR-006-comfyui-storage-constraints]]
