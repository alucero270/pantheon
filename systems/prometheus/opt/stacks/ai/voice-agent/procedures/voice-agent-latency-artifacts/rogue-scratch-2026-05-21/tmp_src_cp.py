import inspect
from qwen_tts.core.models.modeling_qwen3_tts import Qwen3TTSTalkerCodePredictorModelForConditionalGeneration as CPM
src = inspect.getsource(CPM.forward)
for i, l in enumerate(src.splitlines()[:80], 1):
    print(f"{i}: {l}")
