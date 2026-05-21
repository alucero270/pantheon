import inspect
from qwen_tts import Qwen3TTSModel

# Get the full source
src = inspect.getsource(Qwen3TTSModel.generate_custom_voice)
lines = src.split('\n')
for i, line in enumerate(lines):
    print(f'{i+1}: {line}')
