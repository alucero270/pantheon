import torch
from qwen_tts import Qwen3TTSModel
from collections import Counter

model_path = "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice"

m = Qwen3TTSModel.from_pretrained(
    model_path,
    device_map="cuda:0",
    dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
)

wavs, sr = m.generate_custom_voice(text="Warm up.", language="English", speaker="uncle_fu")

talker = m.model.talker

# Check dtypes
dtype_count = Counter()
for n, p in talker.named_parameters():
    dtype_count[str(p.dtype)] += 1
print(f"Parameter dtypes in talker: {dict(dtype_count)}")

# Check specific layer parameters
for n, p in list(talker.model.layers[0].named_parameters())[:5]:
    print(f"  {n}: {p.shape} {p.dtype} {p.device}")

# Check total parameter count
total = sum(p.numel() for p in talker.parameters())
print(f"Total params in talker: {total/1e6:.1f}M")

# Time breakdown of a single layer forward
layer = talker.model.layers[0]
hidden_size = talker.config.hidden_size
device = next(layer.parameters()).device
dtype = next(layer.parameters()).dtype

import time
x = torch.randn(1, 1, hidden_size, device=device, dtype=dtype)
mask = torch.ones(1, 1, dtype=torch.long, device=device)
pos = torch.arange(1, device=device).view(1, 1, -1).expand(3, 1, -1)

torch.cuda.synchronize()
t0 = time.time()
for _ in range(100):
    with torch.no_grad():
        out = layer(x, attention_mask=mask, position_ids=pos, use_cache=True)
torch.cuda.synchronize()
print(f"Single layer forward (100x avg): {(time.time()-t0)/100*1000:.2f}ms")

del m
