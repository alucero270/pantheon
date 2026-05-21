import time
import torch
from qwen_tts import Qwen3TTSModel
import inspect

m = Qwen3TTSModel.from_pretrained(
    "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    device_map="cuda:0",
    dtype=torch.bfloat16,
)
wavs, sr = m.generate_custom_voice(text="Warm up.", language="English", speaker="uncle_fu")

# Check if attention is using custom code
from qwen_tts.core.models.modeling_qwen3_tts import Qwen3TTSTalkerAttention

# Get attention forward source
src = inspect.getsource(Qwen3TTSTalkerAttention.forward)
# Print lines related to flash attention, sdpa, etc.
for i, l in enumerate(src.splitlines()[:80], 1):
    if any(x in l for x in ['attention', 'Attn', 'flash', 'sdpa', 'SDPA', 'torch.nn.functional', 'F.softmax', 'matmul', 'scale']):
        print(f"{i}: {l}")

# Check if we can use FA2 or whatever
attn = m.model.talker.model.layers[0].self_attn
print(f"\nAttention type: {type(attn).__name__}")
print(f"Hidden size: {attn.hidden_size}")
print(f"Num heads: {attn.num_heads}")
print(f"Num KV: {attn.num_key_value_heads}")

del m
