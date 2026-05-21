path = '/home/alex/stacks/voice-agent/pipecat-quickstart/pipecat-quickstart/server/bot.py'
with open(path) as f:
    c = f.read()

c = c.replace(
    '        reuse_context_id_within_turn=False,\n',
    ''
)

with open(path, 'w') as f:
    f.write(c)

with open(path) as f:
    for i, line in enumerate(f, 1):
        if 'reuse_context' in line or 'LLM_MODEL' in line:
            print(f'{i}: {line.rstrip()}')
