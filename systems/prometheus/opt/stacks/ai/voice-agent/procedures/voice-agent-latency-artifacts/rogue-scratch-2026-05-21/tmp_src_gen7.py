import inspect
from qwen_tts.core.models.modeling_qwen3_tts import Qwen3TTSTalkerForConditionalGeneration

src = inspect.getsource(Qwen3TTSTalkerForConditionalGeneration.generate)
lines = src.splitlines()
for i, l in enumerate(lines[80:], 81):
    print(f"{i}: {l}")
