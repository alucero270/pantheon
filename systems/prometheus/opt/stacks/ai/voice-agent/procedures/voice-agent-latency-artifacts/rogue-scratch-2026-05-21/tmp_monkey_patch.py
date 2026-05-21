path = '/home/alex/stacks/voice-agent/voice_api_server.py'
with open(path) as f:
    c = f.read()

# Add monkey-patch after imports (before app = FastAPI())
old = '''from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()'''

new = '''from fastapi.middleware.cors import CORSMiddleware

# Monkey-patch: cache code predictor config to avoid re-init on every TTS call
import qwen_tts.core.models.configuration_qwen3_tts as qwen_config
_original_code_predictor_init = qwen_config.Qwen3TTSTalkerCodePredictorConfig.__init__
_cached_code_predictor = None
def _patched_code_predictor_init(self, **kwargs):
    global _cached_code_predictor
    if _cached_code_predictor is None:
        _original_code_predictor_init(self, **kwargs)
        _cached_code_predictor = self
    else:
        self.__dict__.update(_cached_code_predictor.__dict__)
qwen_config.Qwen3TTSTalkerCodePredictorConfig.__init__ = _patched_code_predictor_init

# Also monkey-patch Qwen3TTSTalkerConfig to cache
_original_talker_config_init = qwen_config.Qwen3TTSTalkerConfig.__init__
_cached_talker_config = None
def _patched_talker_config_init(self, **kwargs):
    global _cached_talker_config
    if _cached_talker_config is None:
        _original_talker_config_init(self, **kwargs)
        _cached_talker_config = self
    else:
        self.__dict__.update(_cached_talker_config.__dict__)
qwen_config.Qwen3TTSTalkerConfig.__init__ = _patched_talker_config_init

app = FastAPI()'''

c = c.replace(old, new)

with open(path, 'w') as f:
    f.write(c)

with open(path) as f:
    for i, line in enumerate(f, 1):
        if 'monkey' in line.lower() or '_patched' in line or '_cached' in line:
            print(f'{i}: {line.rstrip()[:100]}')
