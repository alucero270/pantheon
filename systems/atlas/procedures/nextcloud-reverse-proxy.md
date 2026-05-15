# Nextcloud Behind Traefik

## Service Location

Host: Atlas  
Container: lscr.io/linuxserver/nextcloud  
Port: 8080 (HTTP only)

## Reverse Proxy Flow

Client
  ↓ HTTPS
Prometheus
  ↓ HTTP :8080
Atlas Nextcloud

## Required Nextcloud Settings

trusted_domains:
- nextcloud.home.arpa

trusted_proxies:
- 192.168.60.0/24

overwriteprotocol:
- https

overwritehost:
- nextcloud.home.arpa

overwrite.cli.url:
- https://nextcloud.home.arpa

## Validation

curl -kI https://nextcloud.home.arpa
