import time
import torch
import json

# Don't load from pretrained again, check config first
config_path = "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice/config.json"
with open(config_path) as f:
    config = json.load(f)
tc = config.get("talker_config", {})
print(f"use_cache in talker_config: {tc.get('use_cache', 'NOT SET')}")

# Now load model and benchmark KV cache
from qwen_tts import Qwen3TTSModel
m = Qwen3TTSModel.from_pretrained(
    config_path.replace("/config.json", ""),
    device_map="cuda:0",
    dtype=torch.bfloat16,
)

# Warm up
wavs, sr = m.generate_custom_voice(text="Warm up.", language="English", speaker="uncle_fu")

talker = m.model.talker
hidden_size = talker.config.hidden_size
device = next(talker.parameters()).device
dtype = next(talker.parameters()).dtype

# Test: with KV cache
kv = None
times_with_kv = []
single = torch.randn(1, 1, hidden_size, device=device, dtype=dtype)
for i in range(30):
    torch.cuda.synchronize()
    t0 = time.time()
    with torch.no_grad():
        if kv is None:
            out = talker.model(inputs_embeds=single, use_cache=True)
        else:
            out = talker.model(inputs_embeds=single, past_key_values=kv, use_cache=True)
    torch.cuda.synchronize()
    t = time.time() - t0
    kv = out.past_key_values
    if i >= 5:  # skip warm-up
        times_with_kv.append(t)
print(f"With KV cache: {sum(times_with_kv)/len(times_with_kv)*1000:.1f}ms avg (N={len(times_with_kv)})")

# Test: WITHOUT KV cache (force recompute)
times_no_kv = []
for i in range(10):
    single_new = torch.randn(1, 60, hidden_size, device=device, dtype=dtype)
    torch.cuda.synchronize()
    t0 = time.time()
    with torch.no_grad():
        out = talker.model(inputs_embeds=single_new, use_cache=False)
    torch.cuda.synchronize()
    t = time.time() - t0
    times_no_kv.append(t)
print(f"Without KV cache (seq=60): {sum(times_no_kv)/len(times_no_kv)*1000:.1f}ms avg")

# Test: increasing sequence length WITHOUT KV cache
for seq_len in [10, 20, 40, 80]:
    single_new = torch.randn(1, seq_len, hidden_size, device=device, dtype=dtype)
    torch.cuda.synchronize()
    t0 = time.time()
    with torch.no_grad():
        out = talker.model(inputs_embeds=single_new, use_cache=False)
    torch.cuda.synchronize()
    t = time.time() - t0
    print(f"  Seq={seq_len}: {t*1000:.1f}ms")

del m
