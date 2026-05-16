# Secrets Policy

## Status

Needs decision

## Rules

- Do not commit secrets.
- Do not commit private keys.
- Do not commit passwords.
- Do not commit API tokens.
- Do not commit production Pulumi secrets.
- Do not commit Terraform/OpenTofu state.

## Candidate Secret Systems

- Ansible Vault
- SOPS + age
- 1Password CLI
- Bitwarden CLI
- Pulumi secrets provider
- HashiCorp Vault later

## Decision Required

A final secrets model must be chosen before live automation is introduced.
