# Update voice_api_server.py: QWEN_SPEAKER = "uncle_fu"
path_api = '/home/alex/stacks/voice-agent/voice_api_server.py'
with open(path_api) as f:
    content = f.read()
content = content.replace('QWEN_SPEAKER = "Ryan"', 'QWEN_SPEAKER = "uncle_fu"')
with open(path_api, 'w') as f:
    f.write(content)
print("Updated QWEN_SPEAKER")

# Update bot.py: LLM_MODEL, TTS speed, TTS text_aggregation_mode
path_bot = '/home/alex/stacks/voice-agent/pipecat-quickstart/pipecat-quickstart/server/bot.py'
with open(path_bot) as f:
    content = f.read()

# Change LLM model
content = content.replace('LLM_MODEL = "granite-4.1-8b"', 'LLM_MODEL = "qwen3.5-9b-gpu"')
print("Updated LLM_MODEL")

# Add speed to TTS settings
# Find the TTS block and add settings
old_tts_block = '''    tts = OpenAITTSService(
        base_url=LOCAL_VOICE_API,
        api_key="not-needed",
        voice="alloy",
        text_aggregation_mode=TextAggregationMode.TOKEN,
        model="tts-1",
    )'''

new_tts_block = '''    tts = OpenAITTSService(
        base_url=LOCAL_VOICE_API,
        api_key="not-needed",
        voice="alloy",
        text_aggregation_mode=TextAggregationMode.TOKEN,
        model="tts-1",
        settings=OpenAITTSService.Settings(
            speed=1.3,
        ),
    )'''

content = content.replace(old_tts_block, new_tts_block)
print("Updated TTS settings with speed=1.3")

with open(path_bot, 'w') as f:
    f.write(content)
print("Done")

# Verify
print("\n--- Verifying ---")
with open(path_api) as f:
    for i, line in enumerate(f, 1):
        if 'QWEN_SPEAKER' in line:
            print(f"voice_api_server.py:{i}: {line.rstrip()}")

with open(path_bot) as f:
    for i, line in enumerate(f, 1):
        if 'LLM_MODEL' in line or 'speed' in line or 'text_aggregation' in line:
            print(f"bot.py:{i}: {line.rstrip()}")
