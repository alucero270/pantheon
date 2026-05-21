path = '/home/alex/stacks/voice-agent/pipecat-quickstart/pipecat-quickstart/server/bot.py'
with open(path) as f:
    c = f.read()
c = c.replace('LLM_MODEL = "granite-4.1-8b"', 'LLM_MODEL = "granite-4.1-8b-gpu"')
with open(path, 'w') as f:
    f.write(c)
print("Updated to granite-4.1-8b-gpu")

with open(path) as f:
    for i, line in enumerate(f, 1):
        if 'LLM_MODEL' in line:
            print(f"  Line {i}: {line.rstrip()}")
