import time, torch, numpy as np
from qwen_tts import Qwen3TTSModel

m = Qwen3TTSModel.from_pretrained(
    "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    device_map="cuda:0",
    dtype=torch.bfloat16,
)

# Warm-up call
wavs, sr = m.generate_custom_voice(
    text="Warm up.",
    language="English",
    speaker="uncle_fu",
)

# Use CUDA events for precise timing
start_event = torch.cuda.Event(enable_timing=True)
end_event = torch.cuda.Event(enable_timing=True)

torch.cuda.synchronize()
start_event.record()

wavs, sr = m.generate_custom_voice(
    text="Hello world, this is a test.",
    language="English",
    speaker="uncle_fu",
)

end_event.record()
torch.cuda.synchronize()

elapsed = start_event.elapsed_time(end_event) / 1000
print(f"generate_custom_voice CUDA time: {elapsed:.2f}s")
print(f"Total wall time: {time.time() - t0:.2f}s") if 't0' in dir() else None

audio_len_sec = len(wavs[0]) / sr if sr else 0
print(f"Audio: {len(wavs[0])} samples @ {sr}Hz = {audio_len_sec:.2f}s")

# Now let's benchmark the talker inner loop
print("\n--- Detailed benchmark of talker.generate ---")
_orig_talker_gen = m.model.talker.generate

# Build the inputs manually to avoid retokenization overhead
texts = ["Hello world, this is a test."]
input_ids = [m._tokenize_texts([m._build_assistant_text(t)])[0] for t in texts]

# Prefill
talker_input_embeds, talker_attention_mask, _, _ = m.model._prepare_embeddings_for_text(
    input_ids=input_ids,
    languages=["English"],
    speakers=["uncle_fu"],
    non_streaming_mode=True,
)

# Now let's time individual talker.generate calls with prefill vs generation
torch.cuda.synchronize()
t0 = time.time()

# Call talker.generate once (prefill + generation)
result = m.model.talker.generate(
    inputs_embeds=talker_input_embeds,
    attention_mask=talker_attention_mask,
    max_new_tokens=100,
    do_sample=True,
    top_k=50,
    top_p=1.0,
    temperature=0.9,
    output_hidden_states=True,
    return_dict_in_generate=True,
)

torch.cuda.synchronize()
print(f"Single talker.generate: {time.time()-t0:.2f}s")
print(f"  Sequences shape: {result.sequences.shape}")

del m
