#!/usr/bin/env bash
set -euo pipefail

model_id="qwen3.5-122b-a10b"
response_path="/tmp/qwen122-cpu-moe35-load.json"
exit_path="/tmp/qwen122-cpu-moe35-curl.exit"

rm -f "$response_path" "$exit_path"

pkill -f "llama-server.*${model_id}" 2>/dev/null || true
sleep 2

echo "BEFORE=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

(
  curl -sS --max-time 900 \
    -H "Authorization: Bearer LOCAL" \
    -H "Content-Type: application/json" \
    -d '{"model":"qwen3.5-122b-a10b","messages":[{"role":"user","content":"Reply with exactly OK."}],"max_tokens":8,"temperature":0}' \
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
head -c 2000 "$response_path" 2>/dev/null || true
echo
echo "PROCESS"
pgrep -af "llama-server.*${model_id}" | head -1 || true
