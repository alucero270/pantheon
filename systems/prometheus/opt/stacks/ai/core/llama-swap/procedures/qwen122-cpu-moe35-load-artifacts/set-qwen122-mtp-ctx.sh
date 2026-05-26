#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: $0 <ctx-size>" >&2
  exit 2
fi

ctx_size="$1"
cfg="/mnt/local/nvme/ai/profiles/llama-swap/config.yaml"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
bak="${cfg}.${stamp}.qwen122-mtp-ctx${ctx_size}.bak"

cp "$cfg" "$bak"

awk -v ctx_size="$ctx_size" '
  BEGIN { in_block=0 }
  /^  qwen3\.5-122b-a10b-mtp:/ { in_block=1 }
  /^  gemma-4-26b-a4b-it-mtp-co:/ { in_block=0 }
  in_block && /--ctx-size / { sub(/--ctx-size [0-9]+/, "--ctx-size " ctx_size) }
  { print }
' "$bak" > "$cfg.tmp"

mv "$cfg.tmp" "$cfg"

printf "%s\n" "admin" | sudo -S systemctl restart llama-swap.service >/tmp/qwen122-mtp-ctx-restart.log 2>&1
systemctl is-active llama-swap.service
printf "BACKUP=%s\n" "$bak"
grep -n -A22 'qwen3.5-122b-a10b-mtp:' "$cfg" | sed -n '1,32p'
