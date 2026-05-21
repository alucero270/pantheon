import sys

path = "/home/alex/stacks/voice-agent/venv/lib/python3.12/site-packages/qwen_tts/core/models/modeling_qwen3_tts.py"
with open(path) as f:
    content = f.read()

old = """        talker_codes_list = [talker_codes[i, :length, ] for i, length in enumerate(effective_lengths)]
        talker_hidden_states_list = [talker_hidden_states[i, :length, :] for i, length in enumerate(effective_lengths)]
        
        return talker_codes_list, talker_hidden_states_list"""

new = """        talker_codes_list = [talker_codes[i, :length, ] for i, length in enumerate(effective_lengths)]
        talker_hidden_states_list = [talker_hidden_states[i, :length, :] for i, length in enumerate(effective_lengths)]
        
        import logging as _logging
        _logger = _logging.getLogger('qwen_tts_debug')
        _logger.info('generate: input_tokens=%d generated_tokens=%d effective_lengths=%s',
                     input_ids[0].shape[-1] if input_ids else 0,
                     talker_codes.shape[1] if hasattr(talker_codes, 'shape') else len(talker_codes_list[0]),
                     [int(l) for l in effective_lengths])
        
        return talker_codes_list, talker_hidden_states_list"""

if old in content:
    content = content.replace(old, new, 1)
    with open(path, 'w') as f:
        f.write(content)
    print("Patch applied successfully")
else:
    print("ERROR: old string not found in file")
    sys.exit(1)
