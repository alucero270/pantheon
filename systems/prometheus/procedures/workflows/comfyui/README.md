# ComfyUI Workflow Artifacts

This folder stores ComfyUI workflow artifacts used during Prometheus validation.

These files are reproducibility artifacts, not authoritative creative assets. Generated media remains under `/mnt/local/ssd/ai/outputs/comfy` unless promoted to the approved long-term storage location.

## LTX 2.3

Validated on 2026-05-19 against ComfyUI `0.21.1` on [[systems/prometheus]]:

| Artifact | Purpose | Status |
|---|---|---|
| `unsloth_ltx23_flowers_embedded_ui.json` | UI workflow extracted from `unsloth_flowers.mp4` | Source artifact |
| `unsloth_ltx23_flowers_embedded_api.json` | API prompt extracted from `unsloth_flowers.mp4` | Source artifact |
| `unsloth_ltx23_flowers_udq4ks_ui.json` | UI workflow adapted to the installed distilled `UD-Q4_K_S` model set | Validated by API equivalent |
| `unsloth_ltx23_flowers_udq4ks_api.json` | Full API workflow adapted to the installed distilled `UD-Q4_K_S` model set | Validated |
| `unsloth_ltx23_flowers_udq4ks_smoke_api.json` | Short smoke test variant | Completed prompt `641147e2-774f-4a97-9750-64c31ec6568c` |
| `unsloth_ltx23_high_action_max_udq4ks_api.json` | Full 121-frame high-action render test | Completed prompt `9f8baafc-4811-4470-99d3-2f7ede7a471e` |
| `unsloth_ltx23_high_action_max_udq4ks_ui.json` | UI/canvas version of the full 121-frame high-action render test | Saved for future UI testing |
| `ltx23_gguf_kj_lora_clean_api.json` | Earlier KJ-node smoke test path | Historical validation artifact; active model folders no longer include all referenced files |
| `ltx23_i2v_robot_wave_clean_api.json` | Earlier LTX 2.3 image-to-video API prompt | Historical validation artifact |
| `ltx23_i2v_robot_wave_clean_ui.json` | Earlier LTX 2.3 image-to-video UI workflow | Historical validation artifact |
| `video_ltx2_i2v_distilled.json` | User-provided LTX 2 distilled I2V template | Candidate reference |

## Validated Outputs

| Output | Notes |
|---|---|
| `/mnt/local/ssd/ai/outputs/comfy/codex_smoke/unsloth_ltx23_udq4ks_smoke_00001_.mp4` | 17-frame smoke test |
| `/mnt/local/ssd/ai/outputs/comfy/codex_max/ltx23_high_action_udq4ks_1280x720_121f_24fps_00001_.mp4` | 121-frame high-action test; probed as 1280x704, 24 fps, 5.041667 seconds, H.264 video plus AAC audio |

## Notes

- The Unsloth embedded source workflow referenced the dev `Q4_K_M` model family. The Pantheon validated variant uses the installed distilled `UD-Q4_K_S` model family.
- Use the `_ui.json` artifacts in the ComfyUI canvas. Use the `_api.json` artifacts with the `/prompt` API.
- Longer outputs beyond 121 frames are possible in the workflow graph but remain `Needs validation` under GitHub issue #109.
