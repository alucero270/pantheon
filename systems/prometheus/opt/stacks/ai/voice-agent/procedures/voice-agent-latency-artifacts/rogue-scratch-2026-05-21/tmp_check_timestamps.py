with open('/home/alex/stacks/voice-agent/voice_api_server.log') as f:
    for i, line in enumerate(f):
        if 'code_predictor_config is None' in line:
            print(f'{i+1}: {line[:40]}...')
    f.seek(0)
    print('\n=== Last 15 lines ===')
    lines = f.readlines()
    for line in lines[-15:]:
        print(line.rstrip())
