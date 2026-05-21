p = "/home/alex/stacks/voice-agent/venv/lib/python3.12/site-packages/qwen_tts/core/models/modeling_qwen3_tts.py"
with open(p) as f:
    c = f.read()

old = """        outputs: BaseModelOutputWithPast = self.model(
            input_ids=None,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            cache_position=cache_position,
            **kwargs,
        )

        hidden_states = outputs.last_hidden_state"""

new = """        import time as _tt_mm
        _t0_mm = _tt_mm.time()
        outputs: BaseModelOutputWithPast = self.model(
            input_ids=None,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            cache_position=cache_position,
            **kwargs,
        )
        _dt_mm = _tt_mm.time() - _t0_mm
        if _dt_mm > 0.001:
            import logging as _lg_mm
            _lg_mm.getLogger("qwen_tts_debug").info(f"talker.model() {_dt_mm*1000:.1f}ms use_cache={use_cache}")

        hidden_states = outputs.last_hidden_state"""

if old in c:
    c = c.replace(old, new, 1)
    with open(p, 'w') as f:
        f.write(c)
    print("Timing patch applied")
else:
    print("ERROR: old string not found")
