import json
with open('/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice/config.json') as f:
    d = json.load(f)
talker = d.get('talker_config', {})
spk = talker.get('spk_id', {})
print('Available speakers:', list(spk.keys()))
