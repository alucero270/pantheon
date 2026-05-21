import sys

p = "/home/alex/stacks/voice-agent/venv/lib/python3.12/site-packages/qwen_tts/core/models/modeling_qwen3_tts.py"
with open(p) as f:
    c = f.read()

# The self.model() call in the talker forward (second occurrence)
old = """        outputs: BaseModelOutputWithPast = self.model(
            input_ids=None,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache, """

new = """        import time as _tt_m
        _t0_m = _tt_m.time()
        outputs: BaseModelOutputWithPast = self.model(
            input_ids=None,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache, """

if old in c:
    c = c.replace(old, new, 1)
else:
    print("ERROR: could not find self.model() in talker forward")
    sys.exit(1)

# Add timing log after hidden_states/logits extraction  
old2 = """        hidden_states = outputs.last_hidden_state
        logits = self.codec_head(hidden_states)"""

new2 = """        _dt_m = _tt_m.time() - _t0_m
        if _dt_m > 0.001:
            import logging as _lg_m
            _lg_m.getLogger("qwen_tts_debug").info(f"talker.model() {_dt_m*1000:.1f}ms use_cache={use_cache}")
        hidden_states = outputs.last_hidden_state
        logits = self.codec_head(hidden_states)"""

if old2 in c:
    c = c.replace(old2, new2, 1)
else:
    print("ERROR: could not find hidden_states/logits")
    sys.exit(1)

with open(p, 'w') as f:
    f.write(c)
print("Timing patch applied")
