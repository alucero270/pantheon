import time
import torch
from qwen_tts import Qwen3TTSModel
from qwen_tts.core.models.configuration_qwen3_tts import Qwen3TTSTalkerConfig
from transformers import BitsAndBytesConfig

# Load with explicit attention implementation
model_path = "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice"

config = Qwen3TTSTalkerConfig.from_pretrained(model_path)
print(f"Before: _attn_implementation = {config._attn_implementation}")
config._attn_implementation = "flash_attention_2"
config.update({"attn_implementation": "flash_attention_2"})
print(f"After: _attn_implementation = {config._attn_implementation}")

m = Qwen3TTSModel.from_pretrained(
    model_path,
    config=config,
    device_map="cuda:0",
    dtype=torch.bfloat16,
)

wavs, sr = m.generate_custom_voice(text="Warm up.", language="English", speaker="uncle_fu")

talker = m.model.talker
device = next(talker.parameters()).device
dtype = next(talker.parameters()).dtype
hidden_size = talker.config.hidden_size

# Benchmark single step
dummy = torch.randn(1, 1, hidden_size, device=device, dtype=dtype)
torch.cuda.synchronize()
t0 = time.time()
for _ in range(10):
    with torch.no_grad():
        out = talker.model(inputs_embeds=dummy, use_cache=True)
torch.cuda.synchronize()
t = (time.time() - t0) / 10
print(f"FlashAttn2 single step: {t*1000:.1f}ms")

del m
