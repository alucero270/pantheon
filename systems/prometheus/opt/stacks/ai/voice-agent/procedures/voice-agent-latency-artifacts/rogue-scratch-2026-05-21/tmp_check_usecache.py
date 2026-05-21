import inspect
from qwen_tts.core.models.modeling_qwen3_tts import Qwen3TTSTalkerForConditionalGeneration as TKG

src = inspect.getsource(TKG)
# Find all use_cache references
for i, l in enumerate(src.splitlines(), 1):
    if 'use_cache' in l.lower() and ('#' not in l.split('use_cache')[0] or 1==1):
        print(f"{i}: {l}")
