import torch
from qwen_tts import Qwen3TTSModel

m = Qwen3TTSModel.from_pretrained(
    "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    device_map="cuda:0",
    dtype=torch.bfloat16,
)

# Monkey-patch the talker forward to capture shapes at the generation path
_orig_forward = m.model.talker.forward
import functools

@functools.wraps(_orig_forward)
def _debug_forward(*args, **kwargs):
    if kwargs.get('past_hidden') is not None:
        # Generation path (past_hidden is set)
        input_ids = kwargs.get('input_ids')
        past_hidden = kwargs.get('past_hidden')
        last_id_hidden = m.model.talker.get_input_embeddings()(input_ids)
        print(f"  [DEBUG generation step] input_ids shape={input_ids.shape}")
        print(f"    past_hidden shape={past_hidden.shape}")
        print(f"    last_id_hidden shape={last_id_hidden.shape}")
        
        # Capture the code predictor generate call
        cp = m.model.talker.code_predictor
        predictor_result = cp.generate(
            inputs_embeds=torch.cat((past_hidden, last_id_hidden), dim=1),
            max_new_tokens=m.model.talker.config.num_code_groups - 1,
            do_sample=kwargs.get('subtalker_dosample', True),
            top_p=kwargs.get('subtalker_top_p', 1.0),
            top_k=kwargs.get('subtalker_top_k', 50),
            temperature=kwargs.get('subtalker_temperature', 0.9),
            output_hidden_states=True,
            return_dict_in_generate=True,
        )
        print(f"    predictor_result.sequences shape={predictor_result.sequences.shape}")
        print(f"    sequences={predictor_result.sequences}")
        print(f"    num_code_groups={m.model.talker.config.num_code_groups}")
        
        # Also show codec_hiddens shape
        _seq = predictor_result.sequences
        _codec_hiddens = torch.cat(
            [last_id_hidden]
            + [cp.get_input_embeddings()[i](_seq[..., i:i+1]) for i in range(m.model.talker.config.num_code_groups - 1)],
            dim=1,
        )
        print(f"    codec_hiddens shape={_codec_hiddens.shape}")
    return _orig_forward(*args, **kwargs)

m.model.talker.forward = _debug_forward

# Warm-up
wavs, sr = m.generate_custom_voice(text="Warm up.", language="English", speaker="uncle_fu")
# Reset
m.model.talker.forward = _debug_forward  # reapply after warm-up modifies it

# Test with short input
wavs, sr = m.generate_custom_voice(
    text="Hello.",
    language="English",
    speaker="uncle_fu",
)
print(f"Audio: {len(wavs[0])} samples @ {sr}Hz")
del m
