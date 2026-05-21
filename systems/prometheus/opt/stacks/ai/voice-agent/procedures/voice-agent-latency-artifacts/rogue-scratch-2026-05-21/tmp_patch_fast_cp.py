import sys

path = "/home/alex/stacks/voice-agent/venv/lib/python3.12/site-packages/qwen_tts/core/models/modeling_qwen3_tts.py"
with open(path) as f:
    content = f.read()

old = """            last_id_hidden = self.get_input_embeddings()(input_ids)
            predictor_result = self.code_predictor.generate(
                inputs_embeds=torch.cat((past_hidden, last_id_hidden), dim=1),
                max_new_tokens=self.config.num_code_groups - 1,
                do_sample=subtalker_dosample,
                top_p=subtalker_top_p,
                top_k=subtalker_top_k,
                temperature=subtalker_temperature,
                output_hidden_states=True,
                return_dict_in_generate=True,
            )
            codec_ids = torch.cat((input_ids, predictor_result.sequences), dim=-1)
            codec_hiddens = torch.cat(
                [last_id_hidden]
                + [self.code_predictor.get_input_embeddings()[i](predictor_result.sequences[..., i:i+1]) for i in range(self.config.num_code_groups - 1)],
                dim=1,
            )
            inputs_embeds = codec_hiddens.sum(1, keepdim=True)"""

new = """            last_id_hidden = self.get_input_embeddings()(input_ids)
            # Fast manual code predictor loop (avoids HF generate() overhead)
            cp = self.code_predictor
            n_groups = self.config.num_code_groups
            _cp_inp = torch.cat((past_hidden, last_id_hidden), dim=1)
            _cp_embeds = cp.small_to_mtp_projection(_cp_inp)
            _cp_out = cp.model(
                inputs_embeds=_cp_embeds,
                use_cache=True,
                output_hidden_states=True,
            )
            _cp_hidden = _cp_out.last_hidden_state
            _cp_logits = cp.lm_head[0](_cp_hidden)
            _last_token = _cp_logits[:, -1:]
            _seq_tokens = []
            if subtalker_dosample:
                _probs = torch.softmax(_last_token / subtalker_temperature if subtalker_temperature else _last_token, dim=-1)
                if subtalker_top_k and subtalker_top_k > 0:
                    _topk = _probs.topk(subtalker_top_k, dim=-1)
                    _probs = torch.zeros_like(_probs).scatter_(-1, _topk.indices, _topk.values)
                    _probs = _probs / _probs.sum(dim=-1, keepdim=True)
                _next_id = torch.multinomial(_probs.view(-1, _probs.shape[-1]), num_samples=1).view(_last_token.shape[0], -1)
            else:
                _next_id = _last_token.argmax(dim=-1, keepdim=True)
            _seq_tokens.append(_next_id)
            _cp_kv = _cp_out.past_key_values
            for _step in range(1, n_groups):
                _next_embed = cp.model.get_input_embeddings()[_step - 1](_next_id)
                _next_embed = cp.small_to_mtp_projection(_next_embed)
                _cp_out = cp.model(
                    inputs_embeds=_next_embed,
                    past_key_values=_cp_kv,
                    use_cache=True,
                    output_hidden_states=True,
                )
                _cp_hidden = _cp_out.last_hidden_state
                _cp_logits = cp.lm_head[_step](_cp_hidden)
                _last_token = _cp_logits[:, -1:]
                if subtalker_dosample:
                    _probs = torch.softmax(_last_token / subtalker_temperature if subtalker_temperature else _last_token, dim=-1)
                    if subtalker_top_k and subtalker_top_k > 0:
                        _topk = _probs.topk(subtalker_top_k, dim=-1)
                        _probs = torch.zeros_like(_probs).scatter_(-1, _topk.indices, _topk.values)
                        _probs = _probs / _probs.sum(dim=-1, keepdim=True)
                    _next_id = torch.multinomial(_probs.view(-1, _probs.shape[-1]), num_samples=1).view(_last_token.shape[0], -1)
                else:
                    _next_id = _last_token.argmax(dim=-1, keepdim=True)
                _seq_tokens.append(_next_id)
                _cp_kv = _cp_out.past_key_values
            _sequences = torch.cat(_seq_tokens, dim=-1)
            codec_ids = torch.cat((input_ids, _sequences), dim=-1) if input_ids is not None else _sequences
            codec_hiddens = torch.cat(
                [last_id_hidden]
                + [cp.get_input_embeddings()[i](_sequences[..., i:i+1]) for i in range(n_groups - 1)],
                dim=1,
            )
            inputs_embeds = codec_hiddens.sum(1, keepdim=True)"""

if old in content:
    content = content.replace(old, new, 1)
    with open(path, 'w') as f:
        f.write(content)
    print("Patch applied successfully")
else:
    print("ERROR: old string not found in file")
    # Print similar area for debugging
    import re
    idx = content.find("last_id_hidden = self.get_input_embeddings()(input_ids)")
    if idx >= 0:
        print(f"Found at position {idx}")
        print(content[idx:idx+500])
    else:
        print("String not found anywhere in file")
    sys.exit(1)
