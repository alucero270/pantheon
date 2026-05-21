import json
from qwen_tts.core.models.modeling_qwen3_tts import Qwen3TTSTalkerAttention, ALL_ATTENTION_FUNCTIONS

config_path = "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice/config.json"
with open(config_path) as f:
    config = json.load(f)
tc = config.get("talker_config", {})
print(f"_attn_implementation: {tc.get('_attn_implementation', 'NOT SET')}")
print(f"Available attention functions: {list(ALL_ATTENTION_FUNCTIONS.keys())}")
print(f"model_type: {config.get('model_type')}")
