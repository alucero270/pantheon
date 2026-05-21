import torch
from qwen_tts import Qwen3TTSModel
m = Qwen3TTSModel.from_pretrained("/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice", device_map="cuda:0", dtype=torch.bfloat16)
total = sum(p.numel() for p in m.parameters())
trainable = sum(p.numel() for p in m.parameters() if p.requires_grad)
print(f"Total params: {total/1e9:.2f}B")
print(f"Trainable: {trainable/1e6:.0f}M")
for n, p in list(m.named_parameters())[:5]:
    print(f"  {n}: {p.device} {p.dtype} {p.numel()}")
print("  ...")
for n, p in list(m.named_parameters())[-3:]:
    print(f"  {n}: {p.device} {p.dtype} {p.numel()}")
del m
