import time
import torch

print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"Device count: {torch.cuda.device_count()}")
print(f"Device name: {torch.cuda.get_device_name(0)}")
print(f"CUDA version: {torch.version.cuda}")

# Simplest possible op
a = torch.randn(1000, 1000, device='cuda')
b = torch.randn(1000, 1000, device='cuda')

torch.cuda.synchronize()
t0 = time.time()
for _ in range(100):
    c = a @ b
torch.cuda.synchronize()
t = (time.time() - t0) / 100
print(f"1000x1000 matmul: {t*1000:.3f}ms")

# Very small matmul (like attention)
a2 = torch.randn(1, 16, 1, 128, device='cuda')  # 1 query head
b2 = torch.randn(1, 16, 60, 128, device='cuda')  # 60 KV heads  
torch.cuda.synchronize()
t0 = time.time()
for _ in range(1000):
    c2 = a2 @ b2.transpose(-2, -1)
torch.cuda.synchronize()
t2 = (time.time() - t0) / 1000
print(f"Attention score (Q@K^T): {t2*1000:.3f}ms")

# Even simpler: elementwise add
a3 = torch.randn(1, 1, 2048, device='cuda')
b3 = torch.randn(1, 1, 2048, device='cuda')
torch.cuda.synchronize()
t0 = time.time()
for _ in range(10000):
    c3 = a3 + b3
torch.cuda.synchronize()
t3 = (time.time() - t0) / 10000
print(f"Elementwise add [1,1,2048]: {t3*1000:.4f}ms")

# Linear layer
lin = torch.nn.Linear(2048, 2048, bias=False, device='cuda')
x = torch.randn(1, 1, 2048, device='cuda')
# Warm up
_ = lin(x)
torch.cuda.synchronize()
t0 = time.time()
for _ in range(1000):
    y = lin(x)
torch.cuda.synchronize()
t4 = (time.time() - t0) / 1000
print(f"Linear 2048->2048: {t4*1000:.3f}ms")

# Check if fp16/bf16 helps
lin_fp16 = torch.nn.Linear(2048, 2048, bias=False, device='cuda', dtype=torch.float16)
x_fp16 = torch.randn(1, 1, 2048, device='cuda', dtype=torch.float16)
_ = lin_fp16(x_fp16)
torch.cuda.synchronize()
t0 = time.time()
for _ in range(1000):
    y = lin_fp16(x_fp16)
torch.cuda.synchronize()
t5 = (time.time() - t0) / 1000
print(f"Linear FP16 2048->2048: {t5*1000:.3f}ms")
