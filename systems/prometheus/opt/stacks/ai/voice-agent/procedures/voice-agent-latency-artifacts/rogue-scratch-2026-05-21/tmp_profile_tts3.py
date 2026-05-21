import time
import torch
from qwen_tts import Qwen3TTSModel

m = Qwen3TTSModel.from_pretrained(
    "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    device_map="cuda:0",
    dtype=torch.bfloat16,
)

# Monkey-patch talker.forward with detailed timing
_orig_forward = m.model.talker.forward
_forward_times = []

def _timed_forward(*args, **kwargs):
    _forward_times.append(time.time())
    result = _orig_forward(*args, **kwargs)
    return result
m.model.talker.forward = _timed_forward

# Warm-up
wavs, sr = m.generate_custom_voice(text="Warm up.", language="English", speaker="uncle_fu")

# Reset
_forward_times.clear()

# Test
t0 = time.time()
wavs, sr = m.generate_custom_voice(
    text="Hello world, this is a test.",
    language="English",
    speaker="uncle_fu",
)
total = time.time() - t0

# Calculate timing
n_calls = len(_forward_times)
if n_calls > 1:
    diffs = [_forward_times[i+1] - _forward_times[i] for i in range(n_calls - 1)]
    print(f"Total: {total:.2f}s")
    print(f"forward() calls: {n_calls}")
    print(f"Avg time between calls: {sum(diffs)/len(diffs)*1000:.1f}ms")
    print(f"Min: {min(diffs)*1000:.1f}ms, Max: {max(diffs)*1000:.1f}ms")
    # First call is prefill, rest are generation steps
    if len(diffs) > 1:
        print(f"First (prefill): {diffs[0]*1000:.1f}ms")
        print(f"Generation avg: {sum(diffs[1:])/len(diffs[1:])*1000:.1f}ms ({len(diffs)-1} steps)")

audio_len_sec = len(wavs[0]) / sr
print(f"Audio: {len(wavs[0])} samples @ {sr}Hz = {audio_len_sec:.2f}s")

del m
