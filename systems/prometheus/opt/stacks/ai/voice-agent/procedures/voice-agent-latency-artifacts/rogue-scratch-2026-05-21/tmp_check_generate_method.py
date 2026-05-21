import inspect
from qwen_tts.core.models.modeling_qwen3_tts import Qwen3TTSForConditionalGeneration
src = inspect.getsource(Qwen3TTSForConditionalGeneration.generate)
lines = src.split('\n')
for i, line in enumerate(lines):
    if 'code_predictor' in line.lower() or 'talker_config' in line.lower() or 'Qwen3TTSTalkerConfig' in line or 'Qwen3TTSTalkerCodePredictorConfig' in line:
        print(f'{i+1}: {line}')
# If none found, print first 30 lines
if not any('code_predictor' in l.lower() for l in lines):
    print("No talker config references found, checking _prepare_talker or similar...")
    for name in dir(Qwen3TTSForConditionalGeneration):
        if 'talker' in name.lower() or 'prepare' in name.lower():
            print(f"  Found method: {name}")
