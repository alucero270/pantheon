import inspect
from qwen_tts.core.models.modeling_qwen3_tts import Qwen3TTSForConditionalGeneration

src = inspect.getsource(Qwen3TTSForConditionalGeneration.generate)
for i, l in enumerate(src.splitlines(), 1):
    low = l.lower()
    if any(x in low for x in ["max_new", "do_sample", "temperature", "top_k", "top_p", "repetition"]):
        print(f"{i}: {l}")
