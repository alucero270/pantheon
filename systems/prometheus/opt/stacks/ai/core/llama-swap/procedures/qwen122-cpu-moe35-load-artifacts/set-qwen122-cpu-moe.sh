#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: $0 <n-cpu-moe>" >&2
  exit 2
fi

cpu_moe="$1"
cfg="/mnt/local/nvme/ai/profiles/llama-swap/config.yaml"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
bak="${cfg}.${stamp}.qwen122-cpu-moe${cpu_moe}.bak"

cp "$cfg" "$bak"

awk -v cpu_moe="$cpu_moe" '
  BEGIN { in_block=0 }
  /^  qwen3\.5-122b-a10b:/ { in_block=1 }
  /^  glm-4\.6v:/ { in_block=0 }
  in_block && /--n-cpu-moe / { sub(/--n-cpu-moe [0-9]+/, "--n-cpu-moe " cpu_moe) }
  { print }
' "$bak" > "$cfg.tmp"

mv "$cfg.tmp" "$cfg"

printf "%s\n" "admin" | sudo -S systemctl restart llama-swap.service >/tmp/qwen122-cpu-moe-restart.log 2>&1
systemctl is-active llama-swap.service
printf "BACKUP=%s\n" "$bak"
grep -n -A12 'qwen3.5-122b-a10b:' "$cfg" | sed -n '1,20p'
