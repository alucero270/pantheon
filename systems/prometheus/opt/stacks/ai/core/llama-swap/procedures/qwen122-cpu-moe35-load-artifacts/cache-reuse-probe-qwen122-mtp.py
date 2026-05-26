import json
import time
from urllib import request


URL = "http://172.17.0.1:8085/v1/chat/completions"
HEADERS = {
    "Authorization": "Bearer LOCAL",
    "Content-Type": "application/json",
}
MODEL = "qwen3.5-122b-a10b-mtp"


def call(prompt: str) -> dict:
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 128,
        "temperature": 0,
    }
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(URL, data=body, headers=HEADERS, method="POST")
    start = time.monotonic()
    with request.urlopen(req, timeout=900) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    data["_wall_seconds"] = round(time.monotonic() - start, 3)
    return data


base = "\n".join(f"Stable cache line {i:05d}: keep this prefix identical." for i in range(450))
prompt_1 = base + "\n\nQuestion: Reply with exactly FIRST."
prompt_2 = base + "\n\nQuestion: Reply with exactly SECOND."

for label, prompt in (("FIRST", prompt_1), ("SECOND", prompt_2)):
    result = call(prompt)
    timings = result.get("timings", {})
    message = result["choices"][0]["message"]
    print(json.dumps({
        "label": label,
        "wall_seconds": result["_wall_seconds"],
        "content": message.get("content"),
        "prompt_tokens": result.get("usage", {}).get("prompt_tokens"),
        "completion_tokens": result.get("usage", {}).get("completion_tokens"),
        "prompt_per_second": timings.get("prompt_per_second"),
        "predicted_per_second": timings.get("predicted_per_second"),
        "prompt_ms": timings.get("prompt_ms"),
        "predicted_ms": timings.get("predicted_ms"),
    }, sort_keys=True))
