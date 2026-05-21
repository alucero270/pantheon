import torch

# Check GPU memory from running voice API
print(f"Allocated: {torch.cuda.memory_allocated(0)/1024**3:.2f} GiB")
print(f"Reserved: {torch.cuda.memory_reserved(0)/1024**3:.2f} GiB")
print(f"Max allocated: {torch.cuda.max_memory_allocated(0)/1024**3:.2f} GiB")
print(f"Max reserved: {torch.cuda.max_memory_reserved(0)/1024**3:.2f} GiB")
