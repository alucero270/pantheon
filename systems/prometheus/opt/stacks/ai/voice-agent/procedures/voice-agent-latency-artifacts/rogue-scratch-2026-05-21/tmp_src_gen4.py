import inspect
from qwen_tts.core.models.modeling_qwen3_tts import Qwen3TTSForConditionalGeneration

src = inspect.getsource(Qwen3TTSForConditionalGeneration.generate)
# Print lines 1-130 (full function signature and early body)
for i, l in enumerate(src.splitlines()[:150], 1):
    print(f"{i}: {l}")
