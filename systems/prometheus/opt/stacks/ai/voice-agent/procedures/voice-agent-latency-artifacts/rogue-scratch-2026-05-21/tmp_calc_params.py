import json
d = json.load(open("/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice/config.json"))
tc = d.get("talker_config", {})

# Talker model params
print("=== Talker config ===")
for k in ["hidden_size", "num_hidden_layers", "num_attention_heads", "num_key_value_heads", "intermediate_size", "vocab_size", "max_position_embeddings", "num_code_groups", "text_hidden_size"]:
    print(f"  {k}: {tc.get(k, 'N/A')}")

# Estimate total params
hs = tc.get("hidden_size", 0)
nh = tc.get("num_hidden_layers", 0)
nkv = tc.get("num_key_value_heads", 0)
nah = tc.get("num_attention_heads", 0)
isize = tc.get("intermediate_size", 0)

# QKV projection: hs * (nah + 2*nkv) * hs/hs... actually:
# Q: hs * hs, K: hs * hs*nkv/nah, V: hs * hs*nkv/nah, O: hs * hs
attn_params = hs * hs * (1 + 2*nkv/nah + 1)
mlp_params = 2 * hs * isize  # gate_proj + up_proj + down_proj
rms_params = hs * 4  # 2 RMS norms per layer
total_per_layer = attn_params + mlp_params + rms_params
total_params = nh * total_per_layer
total_params += 2 * hs  # embeddings and lm_head
embedding_params = tc.get("vocab_size", 0) * hs
lm_head_params = tc.get("vocab_size", 0) * hs
print(f"\nEstimated talker params: {total_params/1e9:.2f}B")
print(f"  Per layer: {total_per_layer/1e6:.2f}M")
print(f"  Embedding: {embedding_params/1e6:.2f}M")
print(f"  LM head: {lm_head_params/1e6:.2f}M")
print(f"  Total with embeds: {(total_params + embedding_params + lm_head_params)/1e9:.2f}B")

# Code predictor
cp = tc.get("code_predictor_config", {})
print("\n=== Code Predictor config ===")
for k in ["hidden_size", "num_hidden_layers", "num_attention_heads", "num_key_value_heads", "intermediate_size", "vocab_size", "num_code_groups"]:
    print(f"  {k}: {cp.get(k, 'N/A')}")

cp_hs = cp.get("hidden_size", 0)
cp_nh = cp.get("num_hidden_layers", 0)
cp_nkv = cp.get("num_key_value_heads", 0)
cp_nah = cp.get("num_attention_heads", 0)
cp_isize = cp.get("intermediate_size", 0)
cp_vocab = cp.get("vocab_size", 0)
cp_ng = cp.get("num_code_groups", 16)

cp_attn = cp_hs * cp_hs * (1 + 2*cp_nkv/cp_nah + 1)
cp_mlp = 2 * cp_hs * cp_isize
cp_per_layer = cp_attn + cp_mlp
cp_total = cp_nh * cp_per_layer
cp_total += cp_ng * cp_vocab * cp_hs  # MTP embeddings per code group
cp_total += cp_ng * cp_hs * cp_vocab  # MTP lm heads per code group
cp_total += cp_hs * hs  # small_to_mtp_projection
print(f"Estimated code predictor params: {cp_total/1e6:.2f}M")
