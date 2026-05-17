# Internal DNS Plan (.home.arpa)

## Goal

Remove hosts-file dependency.
Centralize resolution in OPNsense.

## Planned Records

proxy.home.arpa -> Prometheus
nextcloud.home.arpa -> Prometheus
openwebui.home.arpa -> Prometheus
comfy.home.arpa -> Prometheus
searxng.home.arpa -> Prometheus
ollama.home.arpa -> Prometheus (live route observed; needs decision because [[decisions/ADR-007-centralized-ingress-on-prometheus]] says Ollama should remain internal-only)

Future:
jellyfin.home.arpa -> Prometheus

## Authority

OPNsense Unbound DNS:
- Authoritative override for home.arpa

No public DNS required.

## Long-Term

When VPN is added:
VPN clients use OPNsense DNS
Same resolution model continues
No split-brain DNS required.
