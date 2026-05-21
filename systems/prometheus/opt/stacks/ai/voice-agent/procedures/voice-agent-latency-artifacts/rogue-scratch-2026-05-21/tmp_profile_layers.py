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
model = talker.model
device = next(model.parameters()).device
dtype = next(model.parameters()).dtype
hidden_size = model.config.hidden_size

# Monkey-patch decoder layers to time them
layer_times = []
_orig_layers = model.layers
class TimedLayer(torch.nn.Module):
    def __init__(self, idx, orig):
        super().__init__()
        self.idx = idx
        self.orig = orig
    def forward(self, *args, **kwargs):
        torch.cuda.synchronize()
        t = time.time()
        r = self.orig(*args, **kwargs)
        torch.cuda.synchronize()
        dt = time.time() - t
        layer_times.append((self.idx, dt))
        return r

for i, layer in enumerate(model.layers):
    model.layers[i] = TimedLayer(i, layer)

# Run a single forward pass
dummy = torch.randn(1, 1, hidden_size, device=device, dtype=dtype)
layer_times.clear()
with torch.no_grad():
    out = model(inputs_embeds=dummy, use_cache=True)

# Report
per_layer = {}
for idx, dt in layer_times:
    per_layer[idx] = per_layer.get(idx, 0) + dt
print("Per-layer timing (single step, seq=1):")
for idx in sorted(per_layer.keys()):
    ms = per_layer[idx] * 1000
    bar = "#" * int(ms / 2)
    print(f"  Layer {idx:2d}: {ms:.1f}ms {bar}")

total = sum(per_layer.values()) * 1000
print(f"  Total layers: {total:.1f}ms")
print(f"  Number of layers: {len(per_layer)}")

del m
