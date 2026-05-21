import time
import torch
from qwen_tts import Qwen3TTSModel

m = Qwen3TTSModel.from_pretrained(
    "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    device_map="cuda:0",
    dtype=torch.bfloat16,
)

# Pre-warm
t0 = time.time()
wavs1, sr1 = m.generate_custom_voice(
    text="Pre-warm test.",
    language="English",
    speaker="uncle_fu",
)
print(f"Pre-warm: {time.time()-t0:.2f}s len={len(wavs1[0])}")

# Second call
t0 = time.time()
wavs2, sr2 = m.generate_custom_voice(
    text="Hello world, this is a test.",
    language="English",
    speaker="uncle_fu",
)
print(f"Second: {time.time()-t0:.2f}s len={len(wavs2[0])}")

# Profile: just tokenization and text processing
from qwen_tts.core.models.modeling_qwen3_tts import Qwen3TTSForConditionalGeneration

t0 = time.time()
input_ids = [m._tokenize_texts([m._build_assistant_text("Hello world.")])]
print(f"Tokenization: {time.time()-t0:.4f}s")

del m
