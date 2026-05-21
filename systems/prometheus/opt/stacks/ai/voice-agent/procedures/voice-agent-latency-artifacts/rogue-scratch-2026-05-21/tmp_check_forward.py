import inspect
from qwen_tts.core.models.modeling_qwen3_tts import Qwen3TTSForConditionalGeneration
src = inspect.getsource(Qwen3TTSForConditionalGeneration.forward)
# Find where talker_config or code_predictor_config is accessed
lines = src.split('\n')
for i, line in enumerate(lines):
    if 'talker' in line.lower() or 'predictor' in line.lower() or 'config' in line.lower():
        print(f'{i+1}: {line}')
