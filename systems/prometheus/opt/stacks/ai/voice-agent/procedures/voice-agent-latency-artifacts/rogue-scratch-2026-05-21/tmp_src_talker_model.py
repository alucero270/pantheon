import inspect
from qwen_tts.core.models.modeling_qwen3_tts import Qwen3TTSTalkerModel

src = inspect.getsource(Qwen3TTSTalkerModel)
# Just print attention-related methods
for i, l in enumerate(src.splitlines(), 1):
    if 'attention' in l.lower() or 'cache' in l.lower() or 'past_key' in l.lower() or 'forward' in l.strip():
        print(f"{i}: {l}")
