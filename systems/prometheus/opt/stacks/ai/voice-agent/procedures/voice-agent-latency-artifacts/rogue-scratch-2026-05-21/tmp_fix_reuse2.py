path = '/home/alex/stacks/voice-agent/pipecat-quickstart/pipecat-quickstart/server/bot.py'
with open(path) as f:
    c = f.read()

# Add reuse_context_id_within_turn=False after the settings block
old = '''        settings=OpenAITTSService.Settings(
            speed=1.3,
        ),
    )'''

new = '''        settings=OpenAITTSService.Settings(
            speed=1.3,
        ),
        reuse_context_id_within_turn=False,
    )'''

c = c.replace(old, new)

with open(path, 'w') as f:
    f.write(c)

with open(path) as f:
    for i, line in enumerate(f, 1):
        if 'reuse_context' in line:
            print(f'{i}: {line.rstrip()}')
