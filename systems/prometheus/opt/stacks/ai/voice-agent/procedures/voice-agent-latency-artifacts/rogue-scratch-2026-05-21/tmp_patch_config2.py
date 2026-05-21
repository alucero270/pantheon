path = '/home/alex/stacks/voice-agent/voice_api_server.py'
with open(path) as f:
    c = f.read()

old = '''import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voice_api")'''

new = '''import logging
import qwen_tts.core.models.configuration_qwen3_tts as _qc

# Monkey-patch: cache config objects to avoid ~6s re-init on every TTS call
_orig_talker_init = _qc.Qwen3TTSTalkerConfig.__init__
_orig_codec_init = _qc.Qwen3TTSTalkerCodePredictorConfig.__init__
_talker_cache = [None]
_codec_cache = [None]
def _patched_talker(self, **kw):
    if _talker_cache[0] is None:
        _orig_talker_init(self, **kw)
        _talker_cache[0] = self.__dict__.copy()
    else:
        self.__dict__.update(_talker_cache[0])
def _patched_codec(self, **kw):
    if _codec_cache[0] is None:
        _orig_codec_init(self, **kw)
        _codec_cache[0] = self.__dict__.copy()
    else:
        self.__dict__.update(_codec_cache[0])
_qc.Qwen3TTSTalkerConfig.__init__ = _patched_talker
_qc.Qwen3TTSTalkerCodePredictorConfig.__init__ = _patched_codec

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voice_api")'''

c = c.replace(old, new)

with open(path, 'w') as f:
    f.write(c)

with open(path) as f:
    for i, line in enumerate(f, 1):
        if '_patched' in line or '_talker_cache' in line or '_codec_cache' in line or '_orig_' in line:
            print(f'{i}: {line.rstrip()[:100]}')
