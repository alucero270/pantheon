import sys, re

p = "/home/alex/stacks/voice-agent/venv/lib/python3.12/site-packages/qwen_tts/core/models/modeling_qwen3_tts.py"
with open(p) as f:
    c = f.read()

# Find the section in Qwen3TTSForConditionalGeneration.generate() that calls talker.generate
old = """        # forward
        talker_result = self.talker.generate(
            inputs_embeds=talker_input_embeds,
            attention_mask=talker_attention_mask,
            trailing_text_hidden=trailing_text_hiddens,
            tts_pad_embed=tts_pad_embed,
            **talker_kwargs,
        )

        talker_codes = torch.stack([hid[-1] for hid in talker_result.hidden_states if hid[-1] is not None], dim=1)
        talker_hidden_states = torch.cat([hid[0][-1][:, -1:] for hid in talker_result.hidden_states], dim=1)[:, :-1]"""

new = """        # forward — manual generation loop (replaces HF generate() for ~135ms/step savings)
        _tk = talker_kwargs
        _device = talker_input_embeds.device
        _batch = talker_input_embeds.shape[0]
        _dtype = talker_input_embeds.dtype

        def _sample(logits, do_sample, top_k, temperature):
            if do_sample:
                _p = torch.softmax(logits / temperature, dim=-1)
                if top_k and top_k > 0 and top_k < _p.shape[-1]:
                    _top = _p.topk(top_k, dim=-1)
                    _p = torch.zeros_like(_p).scatter_(-1, _top.indices, _top.values)
                return torch.multinomial(_p.view(-1, _p.shape[-1]), num_samples=1).view(logits.shape[0], -1)
            return logits.argmax(dim=-1, keepdim=True)

        # Prefill
        _out = self.talker.forward(
            inputs_embeds=talker_input_embeds,
            attention_mask=talker_attention_mask,
            trailing_text_hidden=trailing_text_hiddens,
            tts_pad_embed=tts_pad_embed,
            subtalker_dosample=_tk.get('subtalker_dosample'),
            subtalker_top_k=_tk.get('subtalker_top_k'),
            subtalker_top_p=_tk.get('subtalker_top_p'),
            subtalker_temperature=_tk.get('subtalker_temperature'),
            use_cache=True,
            output_hidden_states=True,
        )
        _logits = _out.logits[:, -1:, :]
        _pkv = _out.past_key_values
        _ph = _out.past_hidden
        _gs = _out.generation_step
        _all_states = [_out.hidden_states]
        _lh = [(_out.hidden_states[0][-1][:, -1:], _out.hidden_states[1])]

        _suppress = _tk.get('suppress_tokens', [])
        _eos = _tk.get('eos_token_id')
        _max_new = _tk.get('max_new_tokens', 4096)

        # Sample first token
        _t_logits = _logits.clone()
        if _suppress:
            _t_logits[..., _suppress] = float('-inf')
        _next = _sample(_t_logits, _tk.get('do_sample', True), _tk.get('top_k', 50), _tk.get('temperature', 0.9))

        # Make attention mask for first gen step
        _prev_len = talker_attention_mask.shape[1] if talker_attention_mask is not None else talker_input_embeds.shape[1]
        _attn_mask = torch.ones(1, _prev_len + 1, dtype=torch.long, device=_device) if talker_attention_mask is None else torch.cat([talker_attention_mask, torch.ones(1, 1, dtype=torch.long, device=_device)], dim=1)
        _cache_pos = torch.tensor([_prev_len], device=_device)

        for _step in range(_max_new):
            _out = self.talker.forward(
                input_ids=_next,
                past_key_values=_pkv,
                past_hidden=_ph,
                attention_mask=_attn_mask,
                cache_position=_cache_pos,
                trailing_text_hidden=trailing_text_hiddens,
                tts_pad_embed=tts_pad_embed,
                generation_step=_gs,
                subtalker_dosample=_tk.get('subtalker_dosample'),
                subtalker_top_k=_tk.get('subtalker_top_k'),
                subtalker_top_p=_tk.get('subtalker_top_p'),
                subtalker_temperature=_tk.get('subtalker_temperature'),
                use_cache=True,
                output_hidden_states=True,
            )
            _lh.append((_out.hidden_states[0][-1][:, -1:], _out.hidden_states[1]))

            _logits = _out.logits[:, -1:, :]
            _pkv = _out.past_key_values
            _ph = _out.past_hidden
            _gs = _out.generation_step

            # Check EOS
            if _eos is not None and (_next == _eos).any():
                break

            # Sample next token
            _t_logits = _logits.clone()
            if _suppress:
                _t_logits[..., _suppress] = float('-inf')
            _next = _sample(_t_logits, _tk.get('do_sample', True), _tk.get('top_k', 50), _tk.get('temperature', 0.9))

            # Update mask and cache position
            _attn_mask = torch.cat([_attn_mask, torch.ones(1, 1, dtype=torch.long, device=_device)], dim=1)
            _cache_pos = _cache_pos + 1

        talker_codes = torch.stack([h[1] for h in _lh if h[1] is not None], dim=1)
        talker_hidden_states = torch.cat([h[0] for h in _lh], dim=1)[:, :-1]"""

if old in c:
    c = c.replace(old, new, 1)
    with open(p, 'w') as f:
        f.write(c)
    print("Manual talker loop patch applied")
else:
    print("ERROR: old string not found")
    # Show context for debugging
    idx = c.find("talker_result = self.talker.generate(")
    if idx > 0:
        print(f"Found at {idx}, showing context:")
        print(c[idx:idx+500])
    sys.exit(1)
