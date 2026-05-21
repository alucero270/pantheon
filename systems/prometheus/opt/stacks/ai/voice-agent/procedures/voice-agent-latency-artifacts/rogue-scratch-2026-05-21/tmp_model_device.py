import time
import torch
from qwen_tts import Qwen3TTSModel

# Load fresh model
m = Qwen3TTSModel.from_pretrained(
    "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    device_map="cuda:0",
    dtype=torch.bfloat16,
)

# Check device of talker model
print(f"Model device map: {m.hf_device_map if hasattr(m, 'hf_device_map') else 'N/A'}")

# Check specific talker submodule
talker = m.model.talker
print(f"Talker type: {type(talker).__name__}")
for n, p in list(talker.named_parameters())[:3]:
    print(f"  {n}: {p.device} {p.dtype}")
for n, p in list(talker.named_parameters())[-3:]:
    print(f"  {n}: {p.device} {p.dtype}")

# Test with simple input
t0 = time.time()
input_ids = m._tokenize_texts([m._build_assistant_text("Test hello world.")])
print(f"Tokenization: {time.time()-t0:.3f}s")

# Profile just the text embeddings
t0 = time.time()
embeds = m.model.get_text_embeddings()(input_ids[0])
print(f"Text embeddings: {time.time()-t0:.4f}s")

del m
