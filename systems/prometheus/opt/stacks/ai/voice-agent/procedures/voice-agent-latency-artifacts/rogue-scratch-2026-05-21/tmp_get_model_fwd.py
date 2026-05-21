import inspect, sys
sys.path.insert(0, "/home/alex/stacks/voice-agent/venv/lib/python3.12/site-packages")
from qwen_tts.core.models.modeling_qwen3_tts import Qwen3TTSTalkerModel

src = inspect.getsource(Qwen3TTSTalkerModel.forward)
for i, l in enumerate(src.splitlines(), 1):
    print(f"{i}: {l}")
