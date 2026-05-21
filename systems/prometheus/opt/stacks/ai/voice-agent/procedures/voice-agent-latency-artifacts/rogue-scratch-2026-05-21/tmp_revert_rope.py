import sys

p = "/home/alex/stacks/voice-agent/venv/lib/python3.12/site-packages/qwen_tts/core/models/modeling_qwen3_tts.py"
with open(p) as f:
    c = f.read()

# Revert RoPE pre-processing in model forward
old1 = """        # create position embeddings to be shared across the decoder layers
        position_embeddings = self.rotary_emb(hidden_states, position_ids)
        # Pre-process cos/sin for multimodal RoPE once, avoiding per-layer re-processing
        cos, sin = position_embeddings
        mrope_cfg = self.config.rope_scaling
        if mrope_cfg.get("interleaved", False):
            dim = cos.shape[-1]
            modality_num = len(mrope_cfg["mrope_section"])
            _idx_ranges = []
            for i, n in enumerate(mrope_cfg["mrope_section"][1:], 1):
                _idx_ranges.append((i, n * modality_num))
            def _apply_ir(x, modality_num):
                x_t = x[0].clone()
                for beg_idx, end_idx in _idx_ranges:
                    x_t[..., beg_idx:end_idx:modality_num] = x[beg_idx, ..., beg_idx:end_idx:modality_num]
                return x_t
            cos = torch.cat([_apply_ir(cos[..., :dim//2], modality_num)] * 2, dim=-1).unsqueeze(1)
            sin = torch.cat([_apply_ir(sin[..., :dim//2], modality_num)] * 2, dim=-1).unsqueeze(1)
        else:
            mrope_section = mrope_cfg["mrope_section"] * 2
            cos = torch.cat([m[i % 3] for i, m in enumerate(cos.split(mrope_section, dim=-1))], dim=-1).unsqueeze(1)
            sin = torch.cat([m[i % 3] for i, m in enumerate(sin.split(mrope_section, dim=-1))], dim=-1).unsqueeze(1)
        position_embeddings = (cos, sin)"""

new1 = """        # create position embeddings to be shared across the decoder layers
        position_embeddings = self.rotary_emb(hidden_states, position_ids)"""

if old1 in c:
    c = c.replace(old1, new1, 1)
else:
    print("WARNING: could not find RoPE pre-processing section")

# Revert attention forward back to using apply_multimodal_rotary_pos_emb
old2 = """        cos, sin = position_embeddings
        query_states, key_states = (query_states * cos + rotate_half(query_states) * sin,
                                    key_states * cos + rotate_half(key_states) * sin)"""

new2 = """        cos, sin = position_embeddings
        query_states, key_states = apply_multimodal_rotary_pos_emb(
            query_states, key_states, cos, sin, self.rope_scaling["mrope_section"], self.rope_scaling["interleaved"]
        )"""

if old2 in c:
    c = c.replace(old2, new2, 1)
else:
    print("WARNING: could not find inline RoPE in attention")

with open(p, 'w') as f:
    f.write(c)
print("Revert applied")
