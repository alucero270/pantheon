import inspect
from qwen_tts import Qwen3TTSModel

src = inspect.getsource(Qwen3TTSModel.generate_custom_voice)

# Find what happens with the code predictor
lines = src.split('\n')
for i, line in enumerate(lines, 1):
    if 'code_predictor' in line.lower() or 'predictor' in line.lower():
        print(f"Line {i}: {line}")

print("\n--- First 30 lines of generate_custom_voice ---")
for line in lines[:30]:
    print(line)
