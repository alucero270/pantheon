"""Measure voice-agent component latency in a clean, repeatable way.

This script does not patch models or write repo artifacts. By default it checks
the Voice API health endpoint, TTS, and llama-swap LLM latency. STT is optional
because it needs a sanitized local WAV file.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path


def request_json(url: str, timeout: int = 120) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def post_json(url: str, payload: dict, headers: dict | None = None, timeout: int = 120) -> tuple[bytes, dict]:
    body = json.dumps(payload).encode()
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=body, headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), dict(resp.headers)


def post_multipart_audio(url: str, audio_path: Path, timeout: int = 120) -> tuple[bytes, dict]:
    boundary = "----PantheonVoiceAgentBoundary"
    audio = audio_path.read_bytes()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{audio_path.name}"\r\n'
        "Content-Type: audio/wav\r\n\r\n"
    ).encode()
    body += audio
    body += (
        f"\r\n--{boundary}\r\n"
        'Content-Disposition: form-data; name="model"\r\n\r\n'
        "whisper-1\r\n"
        f"--{boundary}--\r\n"
    ).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), dict(resp.headers)


def timed(label: str, func):
    start = time.perf_counter()
    try:
        result = func()
    except Exception as exc:
        elapsed = time.perf_counter() - start
        print(f"{label}: FAIL seconds={elapsed:.3f} error={exc}")
        return None
    elapsed = time.perf_counter() - start
    print(f"{label}: OK seconds={elapsed:.3f}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--voice-api", default="http://127.0.0.1:8002")
    parser.add_argument("--llama-swap", default="http://172.17.0.1:8085/v1")
    parser.add_argument("--llm-model", default="granite-4.1-8b")
    parser.add_argument("--llm-key", default="LOCAL")
    parser.add_argument("--tts-text", default="This is a short voice latency test.")
    parser.add_argument("--tts-non-streaming-mode", choices=["true", "false"])
    parser.add_argument("--tts-max-new-tokens", type=int)
    parser.add_argument("--tts-temperature", type=float)
    parser.add_argument("--tts-top-k", type=int)
    parser.add_argument("--tts-top-p", type=float)
    parser.add_argument("--stt-audio", type=Path)
    args = parser.parse_args()

    print("=== Voice Agent Component Latency ===")
    print(f"voice_api={args.voice_api}")
    print(f"llama_swap={args.llama_swap}")
    print(f"llm_model={args.llm_model}")

    health = timed("health", lambda: request_json(f"{args.voice_api}/health", timeout=30))
    if health:
        print(json.dumps(health, indent=2, sort_keys=True))

    tts_payload = {
        "model": "tts-1",
        "input": args.tts_text,
        "voice": "Ryan",
        "response_format": "wav",
    }
    if args.tts_non_streaming_mode:
        tts_payload["non_streaming_mode"] = args.tts_non_streaming_mode == "true"
    if args.tts_max_new_tokens is not None:
        tts_payload["max_new_tokens"] = args.tts_max_new_tokens
    if args.tts_temperature is not None:
        tts_payload["temperature"] = args.tts_temperature
    if args.tts_top_k is not None:
        tts_payload["top_k"] = args.tts_top_k
    if args.tts_top_p is not None:
        tts_payload["top_p"] = args.tts_top_p

    tts_result = timed(
        "tts",
        lambda: post_json(
            f"{args.voice_api}/v1/audio/speech",
            tts_payload,
        ),
    )
    if tts_result:
        audio, headers = tts_result
        print(f"tts_bytes={len(audio)}")
        for header in ["X-Voice-Generation-Seconds", "X-Voice-Sample-Rate", "X-Voice-Bytes"]:
            if header in headers:
                print(f"{header.lower()}={headers[header]}")

    if args.stt_audio:
        stt_result = timed(
            "stt",
            lambda: post_multipart_audio(f"{args.voice_api}/v1/audio/transcriptions", args.stt_audio),
        )
        if stt_result:
            body, _headers = stt_result
            print(body.decode(errors="replace")[:500])
    else:
        print("stt: SKIP no --stt-audio provided")

    llm_payload = {
        "model": args.llm_model,
        "messages": [{"role": "user", "content": "Reply with one short sentence."}],
        "max_tokens": 40,
    }
    llm_result = timed(
        "llm",
        lambda: post_json(
            f"{args.llama_swap}/chat/completions",
            llm_payload,
            headers={"Authorization": f"Bearer {args.llm_key}"},
        ),
    )
    if llm_result:
        body, _headers = llm_result
        data = json.loads(body)
        print(data["choices"][0]["message"]["content"][:500])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
