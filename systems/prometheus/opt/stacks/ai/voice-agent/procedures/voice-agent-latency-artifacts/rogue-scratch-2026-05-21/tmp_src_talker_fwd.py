import inspect
from qwen_tts.core.models.modeling_qwen3_tts import Qwen3TTSTalkerForConditionalGeneration
src = inspect.getsource(Qwen3TTSTalkerForConditionalGeneration.forward)
for i, l in enumerate(src.splitlines()[:80], 1):
    print(f"{i}: {l}")
