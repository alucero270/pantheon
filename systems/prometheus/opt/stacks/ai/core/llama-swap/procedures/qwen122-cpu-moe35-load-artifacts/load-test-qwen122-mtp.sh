#!/usr/bin/env bash
set -euo pipefail

model_id="qwen3.5-122b-a10b-mtp"
payload_path="/tmp/qwen122-mtp-load-payload.json"
response_path="/tmp/qwen122-mtp-load-response.json"
exit_path="/tmp/qwen122-mtp-load-curl.exit"

rm -f "$payload_path" "$response_path" "$exit_path"

cat > "$payload_path" <<'JSON'
{
  "model": "qwen3.5-122b-a10b-mtp",
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

echo "BEFORE=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

(
  curl -sS --max-time 900 \
    -H "Authorization: Bearer LOCAL" \
    -H "Content-Type: application/json" \
    -d "@${payload_path}" \
    http://172.17.0.1:8085/v1/chat/completions > "$response_path"
  echo "CURL_EXIT=$?" > "$exit_path"
) &
request_pid=$!

for _ in $(seq 1 180); do
  pgrep -af "llama-server.*${model_id}" | head -1 || true
  nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits
  if ! kill -0 "$request_pid" 2>/dev/null; then
    break
  fi
  sleep 5
done

wait "$request_pid" || true

cat "$exit_path" 2>/dev/null || true
echo "RESPONSE_HEAD"
head -c 2500 "$response_path" 2>/dev/null || true
echo
echo "PROCESS"
pgrep -af "llama-server.*${model_id}" | head -1 || true
