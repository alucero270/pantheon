import subprocess
import os

# Check nvidia kernel module version
result = subprocess.run(['modinfo', 'nvidia'], capture_output=True, text=True)
for line in result.stdout.splitlines():
    if 'version' in line.lower():
        print(line)

# Check loaded module
result = subprocess.run(['lsmod'], capture_output=True, text=True)
for line in result.stdout.splitlines():
    if 'nvidia' in line:
        print('lsmod:', line)

# Check nvidia-smi
result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
print('nvidia-smi stderr:', result.stderr[:500])

# Check available .so files
for root, dirs, files in os.walk('/usr/lib'):
    for f in files:
        if 'nvidia-ml' in f:
            print(f'lib: {root}/{f}')

# Check dpkg/rpm for nvidia driver packages
result = subprocess.run(['dpkg', '-l', '*nvidia*'], capture_output=True, text=True)
print(result.stdout[-2000:])
print(result.stderr[-500:])
