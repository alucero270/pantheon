import time
import torch
from qwen_tts import Qwen3TTSModel

model_path = "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice"

m = Qwen3TTSModel.from_pretrained(
    model_path,
    device_map="cuda:0",
    dtype=torch.bfloat16,
)

wavs, sr = m.generate_custom_voice(text="Warm up.", language="English", speaker="uncle_fu")

talker = m.model.talker
device = next(talker.parameters()).device
dtype = next(talker.parameters()).dtype
hidden_size = talker.config.hidden_size

# Time single step
dummy = torch.randn(1, 1, hidden_size, device=device, dtype=dtype)
torch.cuda.synchronize()
t0 = time.time()
for _ in range(10):
    with torch.no_grad():
        out = talker.model(inputs_embeds=dummy, use_cache=True, output_hidden_states=True)
torch.cuda.synchronize()
t = (time.time() - t0) / 10
print(f"Single step (eager attn, RoPE opt): {t*1000:.1f}ms")

# Time 80 token prefill
dummy2 = torch.randn(1, 80, hidden_size, device=device, dtype=dtype)
torch.cuda.synchronize()
t0 = time.time()
for _ in range(10):
    with torch.no_grad():
        out = talker.model(inputs_embeds=dummy2, use_cache=True, output_hidden_states=True)
torch.cuda.synchronize()
t = (time.time() - t0) / 10
print(f"Prefill (seq=80): {t*1000:.1f}ms")

# Run full generate
t0 = time.time()
wavs, sr = m.generate_custom_voice(
    text="Hello world, this is a test of the optimized TTS system.",
    language="English",
    speaker="uncle_fu",
)
print(f"Full generate: {time.time()-t0:.2f}s")
print(f"Audio: {len(wavs[0])} samples @ {sr}Hz = {len(wavs[0])/sr:.2f}s")

del m
