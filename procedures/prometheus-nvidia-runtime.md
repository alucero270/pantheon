---
type: procedure
risk_level: high
last_tested: 2026-01-23
---
# Prometheus NVIDIA GPU Runtime Enablement

## Purpose
Enable NVIDIA GPU acceleration for Docker workloads on Prometheus using the supported NVIDIA driver and NVIDIA Container Toolkit.

---

## Preconditions
- Access required:
  - SSH from MGMT VLAN
  - Sudo privileges
- Systems impacted:
  - Prometheus
- Hardware:
  - NVIDIA RTX A4000 Ada GPU installed

---

## Steps

### 1. Install NVIDIA driver
Identify recommended driver:
```bash
ubuntu-drivers devices
Install recommended driver:

bash
Copy code
sudo apt install -y nvidia-driver-535
sudo reboot
```
### 2. Validate host GPU
```bash
nvidia-smi
```
### 3. Install NVIDIA Container Toolkit

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \ | sudo gpg --dearmor -o /etc/apt/keyrings/nvidia-container-toolkit.gpg

curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \ | sed 's#deb https://#deb [signed-by=/etc/apt/keyrings/nvidia-container-toolkit.gpg] https://#g' \ | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

Install:
```bash
sudo apt update
sudo apt install -y nvidia-container-toolkit
```

Configure Docker runtime:
```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

---

## Validation
Command(s):
```bash
docker run --rm --gpus all \
nvidia/cuda:12.3.0-base-ubuntu22.04 nvidia-smi
```

Expected output:
- GPU visible inside container
- No runtime or OCI errors

---

### Rollback

```bash
sudo apt remove -y nvidia-container-toolkit nvidia-driver-*
sudo reboot
```

---

## Warnings

⚠️ NVIDIA driver updates may require kernel compatibility checks. Always validate after OS upgrades.

---

## Automation Potential
- Partial automation possible
- Reboot requirement prevents full unattended automation

---

## Related Docs
Systems:
[[systems/prometheus]]

ADRs:

[[decisions/ADR-006]]

yaml
Copy code
