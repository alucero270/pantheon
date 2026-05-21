path = '/home/alex/stacks/voice-agent/voice_api_server.py'
with open(path) as f:
    c = f.read()

# Add import time
old = 'import numpy as np'
new = 'import time\nimport numpy as np'
c = c.replace(old, new)

with open(path, 'w') as f:
    f.write(c)

print("Added import time")
