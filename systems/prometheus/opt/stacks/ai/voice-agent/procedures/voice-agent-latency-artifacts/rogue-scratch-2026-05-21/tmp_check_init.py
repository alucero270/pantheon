import inspect
from qwen_tts.core.models.modeling_qwen3_tts import Qwen3TTSForConditionalGeneration
src = inspect.getsource(Qwen3TTSForConditionalGeneration.__init__)
lines = src.split('\n')
for i, line in enumerate(lines):
    print(f'{i+1}: {line}')
