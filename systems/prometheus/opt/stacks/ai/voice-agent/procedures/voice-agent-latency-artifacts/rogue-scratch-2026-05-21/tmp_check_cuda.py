import torch
print(f'torch={torch.__version__} cuda={torch.cuda.is_available()}')
t = torch.randn(100,100).cuda()
print(f'tensor device={t.device}')
print(f'cuda devices={torch.cuda.device_count()}')
print(f'current device={torch.cuda.current_device()}')
print(f'device name={torch.cuda.get_device_name(0)}')
