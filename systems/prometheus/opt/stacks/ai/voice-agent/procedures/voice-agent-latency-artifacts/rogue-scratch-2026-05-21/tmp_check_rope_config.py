import json
d = json.load(open("/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice/config.json"))
tc = d["talker_config"]
print("rope_scaling:", tc.get("rope_scaling"))
print("head_dim:", tc.get("head_dim"))
print("hidden_size:", tc.get("hidden_size"))
