import subprocess, json
r = subprocess.run(['curl', '-s', '-H', 'Authorization: Bearer LOCAL', 'http://localhost:8085/v1/models'], capture_output=True, text=True)
d = json.loads(r.stdout) if r.stdout else {}
for m in d.get('data', []):
    print(m['id'])
