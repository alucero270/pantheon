import inspect
from qwen_tts.core.models.modeling_qwen3_tts import Qwen3TTSForConditionalGeneration

src = inspect.getsource(Qwen3TTSForConditionalGeneration.generate)
lines = src.splitlines()
for i, l in enumerate(lines[150:], 151):
    print(f"{i}: {l}")
