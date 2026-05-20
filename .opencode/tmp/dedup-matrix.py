import re

with open("/mnt/local/nvme/ai/profiles/llama-swap/config.yaml", "r") as f:
    lines = f.readlines()

# Remove duplicate lines in vars section
in_vars = False
in_evict = False
seen_vars = set()
seen_evict = set()
cleaned = []

for line in lines:
    stripped = line.rstrip()
    if stripped == "vars:":
        in_vars = True
        in_evict = False
        seen_vars.clear()
        cleaned.append(line)
        continue
    if stripped == "evict_costs:":
        in_vars = False
        in_evict = True
        seen_evict.clear()
        cleaned.append(line)
        continue
    if stripped == "sets:":
        in_vars = False
        in_evict = False
        cleaned.append(line)
        continue
    if stripped == "models:":
        in_vars = False
        in_evict = False
        cleaned.append(line)
        continue

    if in_vars and stripped.startswith("    "):
        key = stripped.split(":")[0].strip()
        if key in seen_vars:
            continue
        seen_vars.add(key)
    elif in_evict and stripped.startswith("    "):
        key = stripped.split(":")[0].strip()
        if key in seen_evict:
            continue
        seen_evict.add(key)

    cleaned.append(line)

with open("/mnt/local/nvme/ai/profiles/llama-swap/config.yaml", "w") as f:
    f.writelines(cleaned)
print("dedup done")
