path = '/home/alex/stacks/voice-agent/pipecat-quickstart/pipecat-quickstart/server/bot.py'
with open(path) as f:
    content = f.read()

old_import = 'from pipecat.audio.vad.silero import SileroVADAnalyzer'
new_import = old_import + '\nfrom pipecat.services.tts_service import TextAggregationMode'
if old_import in content and 'TextAggregationMode' not in content:
    content = content.replace(old_import, new_import)
    print("Import added")

old_tts = '        voice="alloy",'
new_tts = old_tts + '\n        text_aggregation_mode=TextAggregationMode.TOKEN,'
if old_tts in content and 'text_aggregation_mode' not in content:
    content = content.replace(old_tts, new_tts)
    print("TTS setting added")

with open(path, 'w') as f:
    f.write(content)
print("Done")

for i, line in enumerate(content.split('\n'), 1):
    if 'voice=' in line and 'alloy' in line:
        print(f"Line {i}: {repr(line)}")
    if 'text_aggregation' in line:
        print(f"Line {i}: {repr(line)}")
    if 'TextAggregationMode' in line:
        print(f"Line {i}: {repr(line)}")
