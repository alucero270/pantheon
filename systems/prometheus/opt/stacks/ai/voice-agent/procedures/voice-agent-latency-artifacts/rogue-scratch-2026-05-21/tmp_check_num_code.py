import json
d = json.load(open("/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice/config.json"))
tc = d.get("talker_config", {})
print(f"num_code_groups: {tc.get('num_code_groups', 'NOT FOUND')}")
cp = tc.get("code_predictor_config", {})
print(f"code_predictor_config keys: {len(cp)}")
for k, v in cp.items():
    print(f"  {k}: {v}")
