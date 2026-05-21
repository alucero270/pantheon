import time
import torch
import json

# Test: direct TTS inference timing
from qwen_tts import Qwen3TTSModel

t0 = time.time()
model = Qwen3TTSModel.from_pretrained(
    '/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice',
    device_map='cuda:0',
    dtype=torch.bfloat16,
)
print(f'Model loading: {time.time()-t0:.2f}s')
print(f'Model device: {next(model.model.parameters()).device}')

t0 = time.time()
wavs, sr = model.generate_custom_voice(
    text='Hello world.',
    language='English',
    speaker='uncle_fu',
)
print(f'First TTS: {time.time()-t0:.2f}s')

# Clean up
del model
torch.cuda.empty_cache()

t0 = time.time()
model2 = Qwen3TTSModel.from_pretrained(
    '/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice',
    device_map='cuda:0',
    dtype=torch.bfloat16,
)
print(f'Model loading 2: {time.time()-t0:.2f}s')

t0 = time.time()
wavs, sr = model2.generate_custom_voice(
    text='Hello world.',
    language='English',
    speaker='uncle_fu',
)
print(f'Second TTS (fresh load): {time.time()-t0:.2f}s')

t0 = time.time()
wavs, sr = model2.generate_custom_voice(
    text='This is a test of the TTS system.',
    language='English',
    speaker='uncle_fu',
)
print(f'Third TTS (cached model): {time.time()-t0:.2f}s')
