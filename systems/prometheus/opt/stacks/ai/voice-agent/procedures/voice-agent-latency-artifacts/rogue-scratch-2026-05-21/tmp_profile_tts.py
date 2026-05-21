import time
import torch
from qwen_tts import Qwen3TTSModel

m = Qwen3TTSModel.from_pretrained(
    "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    device_map="cuda:0",
    dtype=torch.bfloat16,
)

# Monkey-patch talker forward to time it
_orig_talker_forward = m.model.talker.forward
def _timed_forward(*args, **kwargs):
    t0 = time.time()
    result = _orig_talker_forward(*args, **kwargs)
    dt = time.time() - t0
    if dt > 0.01:
        print(f"  [TIMED] talker.forward: {dt*1000:.1f}ms input_embeds_shape={kwargs.get('inputs_embeds',args[1] if len(args)>1 else '?').shape if kwargs.get('inputs_embeds',None) is not None else 'N/A'}")
    return result
m.model.talker.forward = _timed_forward

# Also time generate
_orig_gen = m.model.generate
def _timed_gen(*args, **kwargs):
    t0 = time.time()
    result = _orig_gen(*args, **kwargs)
    dt = time.time() - t0
    print(f"  [TIMED] Qwen3TTSForConditionalGeneration.generate: {dt:.2f}s")
    return result
m.model.generate = _timed_gen

# Test
t0 = time.time()
wavs, sr = m.generate_custom_voice(
    text="Hello world, this is a test.",
    language="English",
    speaker="uncle_fu",
)
print(f"Total: {time.time()-t0:.2f}s")

del m
