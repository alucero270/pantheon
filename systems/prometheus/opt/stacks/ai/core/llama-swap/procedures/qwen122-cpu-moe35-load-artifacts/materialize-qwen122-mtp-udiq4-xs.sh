#!/usr/bin/env bash
set -euo pipefail

model_dir="/mnt/local/nvme/ai/models/unsloth/Qwen3.5-122B-A10B-MTP-GGUF/UD-IQ4_XS"
blob_dir="/mnt/local/nvme/ai/cache/huggingface/hub/models--unsloth--Qwen3.5-122B-A10B-MTP-GGUF/blobs"

rm -f \
  "$model_dir/Qwen3.5-122B-A10B-UD-IQ4_XS-00001-of-00003.gguf" \
  "$model_dir/Qwen3.5-122B-A10B-UD-IQ4_XS-00002-of-00003.gguf" \
  "$model_dir/Qwen3.5-122B-A10B-UD-IQ4_XS-00003-of-00003.gguf"

mv "$blob_dir/d312417f4a5ef36ddaffcc4bbdcc47817d0c7bd27f917fa3235ad90b4805c17a" \
  "$model_dir/Qwen3.5-122B-A10B-UD-IQ4_XS-00001-of-00003.gguf"
mv "$blob_dir/5d414ef4dd2b8c73780bafa6b47deb5f5d70ecfa804a785f3b1d98a9084310de" \
  "$model_dir/Qwen3.5-122B-A10B-UD-IQ4_XS-00002-of-00003.gguf"
mv "$blob_dir/d9ac8af93d3818980762fdfb18d4ff30415d37233acba156995bfb816819bcf9" \
  "$model_dir/Qwen3.5-122B-A10B-UD-IQ4_XS-00003-of-00003.gguf"

find "$model_dir" -maxdepth 1 -type f -printf '%s %p\n' | sort -n
echo "SPACE"
df -h / /mnt/local/nvme
echo "DU"
du -sh /mnt/local/nvme/ai/cache/huggingface \
  /mnt/local/nvme/ai/models/unsloth/Qwen3.5-122B-A10B-MTP-GGUF 2>/dev/null
