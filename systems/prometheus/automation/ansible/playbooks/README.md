# Prometheus Ansible Playbooks

## Status

status: scaffold

## Purpose

This folder contains placeholder playbooks for future Prometheus host automation.

## Playbooks

- `prometheus-baseline.yml` - baseline host configuration scaffold
- `prometheus-docker.yml` - Docker host configuration scaffold
- `validate-prometheus.yml` - validation-only scaffold

## Rules

- Do not run playbooks against live hosts without explicit approval.
- Prefer validation before mutation.
- Do not store secrets in playbooks.
- Keep Prometheus-specific playbooks in this folder.
