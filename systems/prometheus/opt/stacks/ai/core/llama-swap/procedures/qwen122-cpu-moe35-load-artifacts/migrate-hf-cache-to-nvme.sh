#!/usr/bin/env bash
set -euo pipefail

src="/home/alex/.cache/huggingface"
dst="/mnt/local/nvme/ai/cache/huggingface"

mkdir -p "$dst"

if [ -d "$src" ] && [ ! -L "$src" ]; then
  shopt -s dotglob nullglob
  mv "$src"/* "$dst"/
  rmdir "$src"
  ln -s "$dst" "$src"
fi

echo "AFTER_MIGRATE"
df -h / /mnt/local/nvme
ls -ld "$src" "$dst"
du -sh "$dst"
