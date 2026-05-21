path = '/home/alex/stacks/voice-agent/pipecat-quickstart/pipecat-quickstart/server/bot.py'
with open(path) as f:
    c = f.read()

# Fix: move observers from PipelineParams to PipelineTask
old = '''    task = PipelineTask(
        pipeline,
        params=PipelineParams(observers=[latency_observer], enable_metrics=True, enable_usage_metrics=True),
    )'''

new = '''    task = PipelineTask(
        pipeline,
        params=PipelineParams(enable_metrics=True, enable_usage_metrics=True),
        observers=[latency_observer],
    )'''

c = c.replace(old, new)

if 'observers=[latency_observer]' not in c or 'observers' in c.split('PipelineParams')[0]:
    # Fallback: try the direct edit approach
    pass

with open(path, 'w') as f:
    f.write(c)

# Verify
with open(path) as f:
    for i, line in enumerate(f, 1):
        if 'observers' in line or 'pipeline' in line.lower() and 'PipelineTask' in line:
            print(f'{i}: {line.rstrip()}')
