import subprocess
r = subprocess.run(['curl', '-v', '-s', '-H', 'Authorization: Bearer LOCAL', 'http://localhost:8085/v1/models'], capture_output=True, text=True)
print('stdout:', r.stdout[:500] if r.stdout else 'empty')
print('stderr:', r.stderr[:500] if r.stderr else 'empty')
print('returncode:', r.returncode)
