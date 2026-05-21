import inspect
from qwen_tts.core.models.configuration_qwen3_tts import Qwen3TTSConfig
src = inspect.getsource(Qwen3TTSConfig.__init__)
lines = src.split('\n')
for i, line in enumerate(lines):
    if 'talker' in line.lower() or 'code_predictor' in line.lower() or 'sub_config' in line.lower():
        print(f'{i+1}: {line}')
# Print first 50 lines for context
print('\n=== First 50 lines ===')
for i, line in enumerate(lines[:50]):
    print(f'{i+1}: {line}')
