import time
import requests

tests = [
    "Hello world.",
    "This is a longer test sentence to measure latency.",
    "Test.",
    "How may I help you today?",
]

for text in tests:
    start = time.time()
    r = requests.post(
        'http://127.0.0.1:8002/v1/audio/speech',
        json={'input': text, 'voice': 'alloy', 'model': 'tts-1', 'response_format': 'wav'},
    )
    elapsed = time.time() - start
    print(f'text="{text[:30]}..." status={r.status_code} size={len(r.content):,}B time={elapsed:.2f}s')
