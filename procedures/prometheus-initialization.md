---
type: procedure
risk_level: medium
last_tested: 2026-01-23
---

# Prometheus Docker Baseline Installation

## Purpose
Install and configure Docker Engine on Prometheus in a clean, reproducible, non-snap manner suitable for disposable compute workloads.

This procedure establishes the **only supported Docker baseline** for Prometheus.

See:
- [[decisions/ADR-006]]
- [[architecture/prometheus]]
- [[systems/prometheus]]

---

## Preconditions
- Access required:
  - SSH access to Prometheus from MGMT VLAN
  - Sudo privileges
- Systems impacted:
  - Prometheus only

---

## Steps

### 1. OS preparation
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg lsb-release
```

Remove any existing Docker packages:
```bash
sudo apt remove -y docker docker-engine docker.io containerd runc || true
```


---

### 2. Add Docker official repository

```bash
sudo install -m 0755 -d /etc/apt/keyrings  curl -fsSL https://download.docker.com/linux/ubuntu/gpg \   | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg  echo \ "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \ https://download.docker.com/linux/ubuntu \ $(lsb_release -cs) stable" \ | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

---

### 3. Install Docker Engine and Compose plugin

```bash
sudo apt update sudo apt install -y \   docker-ce \   docker-ce-cli \   containerd.io \   docker-buildx-plugin \   docker-compose-plugin
```
Enable services:

```bash
sudo systemctl enable --now docker sudo systemctl enable --now containerd
```

---

### 4. Configure non-root access

`sudo usermod -aG docker "$USER" newgrp docker`

---

### 5. Baseline daemon configuration

Create `/etc/docker/daemon.json`:

`{   "live-restore": true,   "userland-proxy": false,   "log-driver": "json-file",   "log-opts": {     "max-size": "10m",     "max-file": "3"   } }`

Restart Docker:

`sudo systemctl restart docker`

---

## Validation

- Command(s):
    
    `docker --version docker compose version docker run --rm hello-world`
    
- Expected output:
    
    - Docker commands succeed without sudo
        
    - `hello-world` container runs successfully
        

---

## Rollback

`sudo systemctl stop docker sudo apt remove -y docker-ce docker-ce-cli containerd.io sudo rm -rf /var/lib/docker /var/lib/containerd`

---

## Warnings

⚠️ Membership in the `docker` group is root-equivalent. Access must be restricted to trusted MGMT users only.

---

## Automation Potential

- Can this be scripted? Yes
    
- Suitable for Ansible or cloud-init during rebuilds
    

---

## Related Docs

- Systems:
    
    - [[systems/prometheus]]
        
- ADRs:
    
    - [[decisions/ADR-006]]
---
