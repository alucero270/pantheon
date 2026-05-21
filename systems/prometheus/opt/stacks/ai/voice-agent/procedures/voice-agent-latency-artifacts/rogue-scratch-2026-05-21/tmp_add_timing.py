path = '/home/alex/stacks/voice-agent/voice_api_server.py'
with open(path) as f:
    c = f.read()

# Add timing to TTS endpoint
old = '''    logger.info(f"TTS: input={req.input[:50]}... voice={req.voice}")

    try:
        result = tts_model.generate_custom_voice('''

new = '''    logger.info(f"TTS: input={req.input[:50]}... voice={req.voice}")
    _t_start = time.time()

    try:
        result = tts_model.generate_custom_voice('''

c = c.replace(old, new)

# Add timing log after TTS success
old = '''        return _tts_response(audio_array, sr, req.response_format)
    except Exception as e:'''

new = '''        _t_elapsed = time.time() - _t_start
        logger.info(f"TTS generate took {_t_elapsed:.2f}s for {len(req.input)} chars")
        return _tts_response(audio_array, sr, req.response_format)
    except Exception as e:'''

c = c.replace(old, new)

with open(path, 'w') as f:
    f.write(c)

print("Timing added")

with open(path) as f:
    for i, line in enumerate(f, 1):
        if '_t_start' in line or '_t_elapsed' in line:
            print(f'{i}: {line.rstrip()}')
