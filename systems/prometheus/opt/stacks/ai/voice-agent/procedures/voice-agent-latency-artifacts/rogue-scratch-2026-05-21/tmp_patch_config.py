path = '/home/alex/stacks/voice-agent/voice_api_server.py'
with open(path) as f:
    c = f.read()

# Replace the monkey-patch with a simpler approach: suppress the logger and cache
old = '''# Monkey-patch: cache code predictor config to avoid re-init on every TTS call
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
qwen_config.Qwen3TTSTalkerConfig.__init__ = _patched_talker_config_init'''

new = '''# Monkey-patch: cache config objects to avoid ~5s re-init on every TTS call
import qwen_tts.core.models.configuration_qwen3_tts as _qc
_orig_cfg_init = _qc.Qwen3TTSTalkerConfig.__init__
_orig_codec_init = _qc.Qwen3TTSTalkerCodePredictorConfig.__init__
def _patch_cfg(self, **kw):
    if not getattr(_qc.Qwen3TTSTalkerConfig, '_patched', False):
        _orig_cfg_init(self, **kw)
        _qc.Qwen3TTSTalkerConfig._patched = True
        _qc.Qwen3TTSTalkerConfig._patched_instance = self
    else:
        self.__dict__.update(_qc.Qwen3TTSTalkerConfig._patched_instance.__dict__)
def _patch_codec(self, **kw):
    if not getattr(_qc.Qwen3TTSTalkerCodePredictorConfig, '_patched', False):
        _orig_codec_init(self, **kw)
        _qc.Qwen3TTSTalkerCodePredictorConfig._patched = True
        _qc.Qwen3TTSTalkerCodePredictorConfig._patched_instance = self
    else:
        self.__dict__.update(_qc.Qwen3TTSTalkerCodePredictorConfig._patched_instance.__dict__)
_qc.Qwen3TTSTalkerConfig.__init__ = _patch_cfg
_qc.Qwen3TTSTalkerCodePredictorConfig.__init__ = _patch_codec'''

c = c.replace(old, new)

with open(path, 'w') as f:
    f.write(c)

with open(path) as f:
    for i, line in enumerate(f, 1):
        if '_patch' in line or '_orig_' in line or '_cached' in line or 'monkey' in line.lower():
            print(f'{i}: {line.rstrip()[:120]}')
