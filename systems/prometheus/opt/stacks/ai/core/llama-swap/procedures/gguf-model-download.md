# llama-swap GGUF Model Download

## Purpose

Download quantized GGUF models from Hugging Face for use with llama-swap backends. This procedure covers downloading multi-part GGUFs from unsloth repos using `huggingface_hub`.

## Requirements

- `huggingface_hub` Python package installed on Prometheus.
- Sufficient free space on `/mnt/local/nvme` (check with `df -h /mnt/local/nvme`).
- Internet access from Prometheus to `huggingface.co`.

## Procedure

### Step 1: List available quant options for a repo

```bash
python3 << 'EOF'
from huggingface_hub import list_repo_files
for f in sorted(list_repo_files("unsloth/MiniMax-M2.7-GGUF")):
    print(f)
EOF
```

This shows all quant folders (e.g., `UD-IQ3_S/`, `UD-IQ4_XS/`, etc.) and their GGUF shards.

### Step 2: Download a specific quant

Create a target directory matching the convention:

```
/mnt/local/nvme/ai/models/gguf/<model-name>-unsloth-ud-<quant>/
```

Then download with `hf_hub_download`:

```python
from huggingface_hub import hf_hub_download
import os, time

repo = "unsloth/MiniMax-M2.7-GGUF"
quant = "UD-IQ3_S"
model_dir = f"/mnt/local/nvme/ai/models/gguf/minimax-m2-7-unsloth-ud-iq3-s"

os.makedirs(f"{model_dir}/{quant}", exist_ok=True)

from huggingface_hub import list_repo_files
files = sorted(f for f in list_repo_files(repo) if f.startswith(f"{quant}/"))

for f in files:
    print(f"Downloading {f}...")
    hf_hub_download(
        repo_id=repo,
        filename=f,
        local_dir=model_dir,
        force_download=False,
    )
```

The download is resumable (HTTP range requests) — if interrupted, re-run and it will resume.

### Step 3: Verify download

```bash
ls -lh /mnt/local/nvme/ai/models/gguf/minimax-m2-7-unsloth-ud-iq3-s/UD-IQ3_S/*.gguf
```

Expected output (example for IQ3_S, 3 parts):
```
-rw-rw-r-- 1 alex alex 7.9M ... MiniMax-M2.7-UD-IQ3_S-00001-of-00003.gguf
-rw-rw-r-- 1 alex alex  47G ... MiniMax-M2.7-UD-IQ3_S-00002-of-00003.gguf
-rw-rw-r-- 1 alex alex  32G ... MiniMax-M2.7-UD-IQ3_S-00003-of-00003.gguf
```

### Step 4: Add model to llama-swap config

Edit `/mnt/local/nvme/ai/profiles/llama-swap/config.yaml` and add a new model entry:

```yaml
your-model-id:
  name: "Human-readable name"
  cmd: >
    ${tq_server} ${common_args}
    --alias your-model-id
    --ctx-size <context-length>
    --batch-size <batch>
    --ubatch-size <ubatch>
    --n-gpu-layers 999
    --model /path/to/00001-of-N.gguf
```

Reload via `watch-config` (auto, ~5s) or restart the service.

## Reference: Downloaded Models

| Model | Quant | Date | Parts | Total Size |
|---|---|---|---|---|
| MiniMax-M2.7 | UD-IQ3_S | 2026-05-29 | 3 | ~79 GiB |
| MiniMax-M2.7 | UD-IQ3_XXS | 2026-05-25 | 3 | ~75 GiB |

## Notes

- Download speed is typically 30-35 MiB/s on Prometheus's connection.
- Part 1 is always small (metadata), parts 2+ are the actual weights.
- Always reference shard `00001-of-N` in the model path — llama-server auto-discovers sibling shards.
- See [[systems/prometheus/inventory]] for the full model manifest.
