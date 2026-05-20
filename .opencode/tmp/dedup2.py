import sys

with open("/mnt/local/nvme/ai/profiles/llama-swap/config.yaml") as f:
    lines = f.readlines()

out = []
seen = {"vars": set(), "evict_costs": set()}
section = None

for line in lines:
    s = line.strip()
    if s in ("vars:", "evict_costs:"):
        section = s.rstrip(":")
        out.append(line)
    elif s in ("models:", "apiKeys:", "macros:", "matrix:"):
        section = None
        out.append(line)
    elif section and ":" in line and line.startswith("    "):
        key = line.split(":")[0].strip()
        if key in seen[section]:
            continue
        seen[section].add(key)
        out.append(line)
    else:
        out.append(line)

with open("/mnt/local/nvme/ai/profiles/llama-swap/config.yaml", "w") as f:
    f.writelines(out)
print("cleaned", len(lines) - len(out), "duplicates")
