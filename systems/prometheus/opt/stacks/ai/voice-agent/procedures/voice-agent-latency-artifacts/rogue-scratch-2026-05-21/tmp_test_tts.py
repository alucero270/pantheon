import subprocess
import json

req = json.dumps({"model": "tts-1", "input": "Hello world, this is a test of the TTS system.", "voice": "alloy"})
result = subprocess.run([
    "curl", "-s", "-X", "POST",
    "http://localhost:8002/v1/audio/speech",
    "-H", "Content-Type: application/json",
    "-d", req,
    "-o", "/tmp/tts_test_output.wav",
    "-w", "HTTP %{http_code} Time %{time_total}s Size %{size_download}B"
], capture_output=True, text=True, timeout=30)
print(result.stdout)
print(result.stderr[:200] if result.stderr else "")

import os
if os.path.exists("/tmp/tts_test_output.wav"):
    sz = os.path.getsize("/tmp/tts_test_output.wav")
    print(f"Output WAV size: {sz} bytes")
