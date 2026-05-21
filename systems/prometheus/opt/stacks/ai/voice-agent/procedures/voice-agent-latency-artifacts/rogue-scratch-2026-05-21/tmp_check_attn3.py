import json
config_path = "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice/config.json"
with open(config_path) as f:
    config = json.load(f)
tc = config.get("talker_config", {})
print(f"_attn_implementation: {tc.get('_attn_implementation', 'NOT SET')}")

# Also check the ALL_ATTENTION_FUNCTIONS keys from the model file
import sys
sys.path.insert(0, "/home/alex/stacks/voice-agent/venv/lib/python3.12/site-packages")
from qwen_tts.core.models.modeling_qwen3_tts import ALL_ATTENTION_FUNCTIONS
print(f"Available: {list(ALL_ATTENTION_FUNCTIONS.keys())}")
