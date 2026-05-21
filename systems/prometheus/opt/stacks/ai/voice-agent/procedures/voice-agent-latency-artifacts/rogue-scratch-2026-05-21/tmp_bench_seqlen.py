import time
import torch
from qwen_tts import Qwen3TTSModel

m = Qwen3TTSModel.from_pretrained(
    "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    device_map="cuda:0",
    dtype=torch.bfloat16,
)

wavs, sr = m.generate_custom_voice(text="Warm up.", language="English", speaker="uncle_fu")

talker = m.model.talker
device = next(talker.parameters()).device
dtype = next(talker.parameters()).dtype
hidden_size = talker.config.hidden_size

# Benchmark just the model's __init__ overhead
# Test tiny vs large inputs to find the fixed-cost floor
for seq_len in [1, 10, 100, 1000]:
    dummy = torch.randn(1, seq_len, hidden_size, device=device, dtype=dtype)
    torch.cuda.synchronize()
    t0 = time.time()
    with torch.no_grad():
        out = talker.model(inputs_embeds=dummy, use_cache=True)
    torch.cuda.synchronize()
    print(f"Seq={seq_len:5d}: {(time.time()-t0)*1000:.1f}ms")

# What if we bypass the model entirely and just do a single linear layer?
lin = torch.nn.Linear(hidden_size, hidden_size, bias=False, device=device, dtype=dtype)
dummy = torch.randn(1, 1, hidden_size, device=device, dtype=dtype)
torch.cuda.synchronize()
t0 = time.time()
for _ in range(1000):
    _ = lin(dummy)
torch.cuda.synchronize()
print(f"Single linear: {(time.time()-t0)*1000:.3f}ms per call")

# What about 28 linear layers (simulating the model)?
torch.cuda.synchronize()
t0 = time.time()
for _ in range(1000):
    x = dummy
    for _ in range(28):
        x = lin(x)
torch.cuda.synchronize()
print(f"28 linears: {(time.time()-t0)*1000:.3f}ms per call")

del m
