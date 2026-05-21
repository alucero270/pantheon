import inspect
from qwen_tts.core.models.modeling_qwen3_tts import apply_multimodal_rotary_pos_emb

src = inspect.getsource(apply_multimodal_rotary_pos_emb)
for i, l in enumerate(src.splitlines(), 1):
    print(f"{i}: {l}")
