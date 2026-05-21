import inspect
from qwen_tts import Qwen3TTSModel
src = inspect.getsource(Qwen3TTSModel._merge_generate_kwargs)
for i, l in enumerate(src.splitlines(), 1):
    print(f"{i}: {l}")
