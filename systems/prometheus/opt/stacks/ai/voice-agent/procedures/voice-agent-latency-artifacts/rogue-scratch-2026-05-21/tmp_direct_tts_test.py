import subprocess, json
data = {"input": "Hello world.", "voice": "alloy", "model": "tts-1", "response_format": "wav"}
r = subprocess.run(
    ['curl', '-s', '-X', 'POST', 'http://127.0.0.1:8002/v1/audio/speech',
     '-H', 'Content-Type: application/json',
     '-d', json.dumps(data)],
    capture_output=True
)
print(f'Status: {r.returncode}, stdout bytes: {len(r.stdout)}, stderr bytes: {len(r.stderr)}')
if r.stderr:
    print(f'stderr: {r.stderr[:200]}')
import sys
sys.stdout.buffer.write(r.stdout[:100])
