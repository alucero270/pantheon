path = '/home/alex/stacks/voice-agent/voice_api_server.py'
with open(path) as f:
    c = f.read()

# Add pre-warm call after model loading
old = '''    logger.info("Qwen3-TTS loaded")'''
new = '''    logger.info("Qwen3-TTS loaded")
    # Pre-warm: make a dummy TTS call to initialize code predictor caches
    logger.info("Pre-warming TTS model...")
    try:
        tts_model.generate_custom_voice(
            text="Pre-warm.",
            language="English",
            speaker=QWEN_SPEAKER,
        )
        logger.info("TTS pre-warm complete")
    except Exception as e:
        logger.warning(f"TTS pre-warm failed (non-critical): {e}")'''

c = c.replace(old, new)

with open(path, 'w') as f:
    f.write(c)

# Verify
with open(path) as f:
    for i, line in enumerate(f, 1):
        if 'Pre-warm' in line or 'pre-warm' in line:
            print(f'{i}: {line.rstrip()}')
