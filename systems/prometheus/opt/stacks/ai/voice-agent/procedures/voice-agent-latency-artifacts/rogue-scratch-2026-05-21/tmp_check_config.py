import json
f = open("/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice/config.json")
d = json.load(f)
f.close()

keys = [k for k in d.keys() if any(x in k.lower() for x in ["codec", "vocab", "eos", "pad", "bos", "tts", "talker", "code_predictor"])]
for k in keys:
    v = d[k]
    if isinstance(v, dict):
        print(f"{k}:")
        for sk, sv in v.items():
            if any(x in sk.lower() for x in ["codec", "vocab", "eos", "pad", "bos", "tts", "max", "min"]):
                print(f"  {sk}: {sv}")
    else:
        print(f"{k}: {v}")
