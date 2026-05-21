import inspect
from qwen_tts.core.models.modeling_qwen3_tts import Qwen3TTSTalkerAttention

# Get the full forward method
src = inspect.getsource(Qwen3TTSTalkerAttention.forward)
for i, l in enumerate(src.splitlines()[:100], 1):
    print(f"{i}: {l}")
