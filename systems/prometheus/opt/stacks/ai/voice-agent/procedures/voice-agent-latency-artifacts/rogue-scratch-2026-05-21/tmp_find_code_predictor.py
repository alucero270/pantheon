import os
pkg = '/home/alex/stacks/voice-agent/venv/lib/python3.12/site-packages/qwen_tts'
for root, dirs, files in os.walk(pkg):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path) as fh:
                for i, line in enumerate(fh, 1):
                    if 'code_predictor_config' in line:
                        print(f'{os.path.relpath(path, pkg)}:{i}: {line.rstrip()[:150]}')
