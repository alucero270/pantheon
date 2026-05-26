#!/usr/bin/env bash
set -euo pipefail

cfg="/mnt/local/nvme/ai/profiles/llama-swap/config.yaml"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
bak="${cfg}.${stamp}.qwen122-mtp-cache-tuning.bak"

cp "$cfg" "$bak"

python3 - <<'PY'
from pathlib import Path

cfg = Path("/mnt/local/nvme/ai/profiles/llama-swap/config.yaml")
text = cfg.read_text()
start = text.index("  qwen3.5-122b-a10b-mtp:\n")
end = text.index("  gemma-4-26b-a4b-it-mtp-co:\n", start)
block = text[start:end]

for flag in ("--cache-ram", "--ctx-checkpoints", "--checkpoint-every-n-tokens"):
    lines = [line for line in block.splitlines() if flag not in line]
    block = "\n".join(lines) + "\n"

anchor = "      --reasoning-budget 64\n"
insert = (
    "      --cache-ram 16384\n"
    "      --ctx-checkpoints 64\n"
    "      --checkpoint-every-n-tokens 4096\n"
)
if anchor not in block:
    raise SystemExit("reasoning-budget anchor not found in qwen122 MTP block")
block = block.replace(anchor, anchor + insert)
cfg.write_text(text[:start] + block + text[end:])
PY

printf "%s\n" "admin" | sudo -S systemctl restart llama-swap.service >/tmp/qwen122-mtp-cache-tuning-restart.log 2>&1
systemctl is-active llama-swap.service
printf "BACKUP=%s\n" "$bak"
grep -n -A24 'qwen3.5-122b-a10b-mtp:' "$cfg" | sed -n '1,36p'
