import time
import torch
import numpy as np

from qwen_tts import Qwen3TTSModel

m = Qwen3TTSModel.from_pretrained(
    "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    device_map="cuda:0",
    dtype=torch.bfloat16,
)

# Monkey-patch the talker generate to log token count
_orig_gen = m.model.talker.generate
def _debug_gen(*args, **kwargs):
    t0 = time.time()
    result = _orig_gen(*args, **kwargs)
    dt = time.time() - t0
    # Count generated tokens
    n_tokens = len(result.sequences[0]) - result.sequences.shape[1]
    print(f"  [DEBUG] talker.generate: {dt:.2f}s for {n_tokens} tokens (input len={result.sequences.shape[1]})")
    return result
m.model.talker.generate = _debug_gen

# Test
t0 = time.time()
wavs, sr = m.generate_custom_voice(
    text="Hello world, this is a test.",
    language="English",
    speaker="uncle_fu",
)
print(f"Total: {time.time()-t0:.2f}s, audio len={len(wavs[0])}, sr={sr}")

del m
