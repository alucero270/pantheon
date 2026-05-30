import yaml

with open("/mnt/local/nvme/ai/profiles/llama-swap/config.yaml", "r") as f:
    data = yaml.safe_load(f)

# Rebuild matrix vars deduplicated
data["matrix"]["vars"]["g26m"] = "gemma-4-26b-a4b-it-mtp"
data["matrix"]["vars"]["g31m"] = "gemma-4-31b-it-mtp"  # IQ3_XXS, non-MTP, ~14 GiB VRAM
data["matrix"]["vars"]["q35m"] = "qwen3.6-35b-a3b-mtp"

# Rebuild evict_costs deduplicated
data["matrix"]["evict_costs"]["g26m"] = 5
data["matrix"]["evict_costs"]["g31m"] = 10
data["matrix"]["evict_costs"]["q35m"] = 5

# Update colocated set
old_set = data["matrix"]["sets"]["colocated"]
new_set = old_set.replace("(g26 | g31 |", "(g26 | g26m | g31 | g31m |")
new_set = new_set.replace("q35 |", "q35 | q35m |")
data["matrix"]["sets"]["colocated"] = new_set

with open("/mnt/local/nvme/ai/profiles/llama-swap/config.yaml", "w") as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

print("matrix rebuilt cleanly")
