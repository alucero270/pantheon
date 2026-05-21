import inspect
from qwen_tts.core.models.configuration_qwen3_tts import Qwen3TTSTalkerConfig
src = inspect.getsource(Qwen3TTSTalkerConfig.__init__)
for i, line in enumerate(src.split('\n'), 1):
    print(f'{i}: {line}')
