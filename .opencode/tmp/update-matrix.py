import re

with open("/mnt/local/nvme/ai/profiles/llama-swap/config.yaml", "r") as f:
    content = f.read()

vars_line = "    q27m: qwen3.6-27b-mtp"
vars_extra = (
    "\n    g26m: gemma-4-26b-a4b-it-mtp"
    "\n    g31m: gemma-4-31b-it-mtp"  # IQ3_XXS, non-MTP, ~14 GiB VRAM
    "\n    q35m: qwen3.6-35b-a3b-mtp"
)
content = content.replace(vars_line, vars_line + vars_extra)

evict_line = "    q9: 1"
evict_extra = (
    "\n    g26m: 5"
    "\n    g31m: 10"
    "\n    q35m: 5"
)
content = content.replace(evict_line, evict_line + evict_extra)

old_set = "(g26 | g31 | q122 | g4v | gf4 | gr30 | n2 | n3 | mx8 | mx9 | mx12 | q35 | q27 | q27m)"
new_set = "(g26 | g26m | g31 | g31m | q122 | g4v | gf4 | gr30 | n2 | n3 | mx8 | mx9 | mx12 | q35 | q35m | q27 | q27m)"
content = content.replace(old_set, new_set)

with open("/mnt/local/nvme/ai/profiles/llama-swap/config.yaml", "w") as f:
    f.write(content)
print("matrix updated")
