#!/usr/bin/env bash
set -euo pipefail

model_file="/mnt/local/nvme/ai/models/unsloth/Qwen3.5-122B-A10B-MTP-GGUF/Qwen3.5-122B-A10B-UD-IQ3_XXS.gguf"
blob_file="/mnt/local/nvme/ai/cache/huggingface/hub/models--unsloth--Qwen3.5-122B-A10B-MTP-GGUF/blobs/998a8924ff6a12661b60b898553f1771ed1c22c8bfe75e5c8a6f47d01776becc"

if [ -L "$model_file" ]; then
  rm "$model_file"
fi

if [ -f "$blob_file" ]; then
  mv "$blob_file" "$model_file"
fi

ls -lh "$model_file"
echo "DU"
du -sh /mnt/local/nvme/ai/cache/huggingface \
  /mnt/local/nvme/ai/models/unsloth/Qwen3.5-122B-A10B-MTP-GGUF 2>/dev/null
