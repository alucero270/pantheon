path = '/home/alex/stacks/voice-agent/pipecat-quickstart/pipecat-quickstart/server/bot.py'
with open(path) as f:
    c = f.read()

c = c.replace(
    '        reuse_context_id_within_turn: bool = True,\n    )',
    '        reuse_context_id_within_turn=False,\n    )',
    1
)

with open(path, 'w') as f:
    f.write(c)

with open(path) as f:
    for i, line in enumerate(f, 1):
        if 'reuse_context_id' in line:
            print(f'{i}: {line.rstrip()}')
