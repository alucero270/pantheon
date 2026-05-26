#!/usr/bin/env bash
set -euo pipefail

payload_path="/tmp/qwen122-content-probe.json"
response_path="/tmp/qwen122-content-response.json"

cat > "$payload_path" <<'JSON'
{
  "model": "qwen3.5-122b-a10b",
  "messages": [
    {
      "role": "user",
      "content": "Reply with exactly OK and no other text."
    }
  ],
  "max_tokens": 128,
  "temperature": 0
}
JSON

curl -sS --max-time 180 \
  -H "Authorization: Bearer LOCAL" \
  -H "Content-Type: application/json" \
  -d "@${payload_path}" \
  http://172.17.0.1:8085/v1/chat/completions > "$response_path"

head -c 2000 "$response_path"
echo
nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader
