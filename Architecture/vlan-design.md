# VLAN Design

## VLANs

| VLAN | Name | Purpose |
|-----:|------|--------|
| 10 | EXPOSED | Public-facing services |
| 20 | USER | Trusted user devices |
| 30 | IOT | IoT devices |
| 40 | GUEST | Guest Wi-Fi |
| 50 | UNTRUSTED | Quarantine / testing |
| 60 | SERVERS | Internal servers |
| 99 | MGMT | Infrastructure management |

## Design Rules

- No lateral movement by default
- USER Wi-Fi cannot access MGMT or infrastructure
- SERVERS VLAN is not directly reachable from USER
