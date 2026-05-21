import time
import torch
from qwen_tts import Qwen3TTSModel

m = Qwen3TTSModel.from_pretrained(
    "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    device_map="cuda:0",
    dtype=torch.bfloat16,
)

# Warm up
wavs, sr = m.generate_custom_voice(text="Warm up.", language="English", speaker="uncle_fu")

# Simple timing of a single forward pass through talker.model
talker = m.model.talker
device = next(talker.parameters()).device
dtype = next(talker.parameters()).dtype

# Create a dummy input
hidden_size = talker.config.hidden_size
batch = 1
seq_len = 60  # typical prefill length

dummy_embeds = torch.randn(batch, seq_len, hidden_size, device=device, dtype=dtype)
dummy_mask = torch.ones(batch, seq_len, device=device, dtype=torch.long)

# Warm up the talker.model (the transformer)
for _ in range(3):
    with torch.no_grad():
        _ = talker.model(inputs_embeds=dummy_embeds, use_cache=True)

# Time prefill
torch.cuda.synchronize()
t0 = time.time()
for _ in range(10):
    with torch.no_grad():
        out = talker.model(inputs_embeds=dummy_embeds, use_cache=True, output_hidden_states=True)
torch.cuda.synchronize()
t_prefill = (time.time() - t0) / 10
print(f"Prefill (seq=60): {t_prefill*1000:.1f}ms")

# Time single token forward (generation step)
kv = out.past_key_values
single_embeds = torch.randn(batch, 1, hidden_size, device=device, dtype=dtype)

torch.cuda.synchronize()
t0 = time.time()
for _ in range(50):
    with torch.no_grad():
        out2 = talker.model(inputs_embeds=single_embeds, past_key_values=kv, use_cache=True, output_hidden_states=True)
    kv = out2.past_key_values
torch.cuda.synchronize()
t_gen = (time.time() - t0) / 50
print(f"Single gen step: {t_gen*1000:.1f}ms")

# Check if flash attention is being used
print(f"Flash attn: {torch.backends.cuda.flash_sdp_enabled()}")
print(f"Memory efficient: {torch.backends.cuda.mem_efficient_sdp_enabled()}")
print(f"Device: {device}, dtype: {dtype}")

del m
