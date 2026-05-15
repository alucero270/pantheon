# Architecture

## Purpose

This folder contains cross-system architecture documents for Pantheon.

Architecture documents define system boundaries, network design, data ownership, security constraints, ingress, DNS, remote access, and other design models that affect more than one system.

## Current Documents

- [[architecture/overview]]
- [[architecture/network-architecture]]
- [[architecture/vlan-design]]
- [[architecture/security-model]]
- [[architecture/data-strategy]]
- [[architecture/dns-plan]]
- [[architecture/network-Ingress-Flow]]
- [[architecture/media-architecture]]
- [[architecture/second-brain-chatgpt-obsidian]]

## Templates

- Folder-local template: [[architecture/architecture-template]]
- Shared fallback templates: [[templates/README]]

## Rules

- Architecture changes may require an ADR in [[decisions/README]].
- Do not weaken locked VLAN, security, storage, or management constraints.
- Do not convert future plans into implemented facts.
- Use `TBD`, `Unknown`, or `Needs validation` where evidence is missing.

## Pass 2 Notes

- Folder name casing is currently `Architecture` in the working tree and should be normalized to lowercase only during an approved restructure step.
- `network-Ingress-Flow.md` uses mixed case and should be reviewed for kebab-case normalization.
