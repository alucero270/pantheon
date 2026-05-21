path = '/home/alex/stacks/voice-agent/pipecat-quickstart/pipecat-quickstart/server/bot.py'
with open(path) as f:
    content = f.read()

# Revert LLM model
content = content.replace('LLM_MODEL = "qwen3.5-9b-gpu"', 'LLM_MODEL = "granite-4.1-8b"')

# Remove text_aggregation_mode line entirely (revert to default = SENTENCE)
content = content.replace('\n        text_aggregation_mode=TextAggregationMode.TOKEN,', '')

# Remove import of TextAggregationMode since no longer needed
content = content.replace('from pipecat.services.tts_service import TextAggregationMode\n', '')

with open(path, 'w') as f:
    f.write(content)
print("Done reverting")

for i, line in enumerate(content.split('\n'), 1):
    if 'LLM_MODEL' in line or 'text_aggregation' in line or 'TextAggregation' in line or 'speed=' in line:
        print(f'{i}: {line}')