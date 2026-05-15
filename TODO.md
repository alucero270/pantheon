# Branch Validation Queue

## Purpose

This document tracks branches that may contain useful Pantheon work but require validation before merge.

No branch listed here is approved for merge by default.

## Validation Rules

- Compare each branch against `main`.
- Use commit history and diff evidence only.
- Do not merge during this pass.
- Do not delete branches during this pass.
- Do not rewrite branch history.
- Mark unclear branches as `Needs review` or `Unknown`.
- Create follow-up issues for validation work when appropriate.

## Branch Inventory

| Branch | Compared Against | Summary | Changed Areas | Risk Level | Merge Candidate | Required Validation | Notes |
|---|---|---|---|---|---|---|---|
| `add_modify_llm_models` | `main` | No commits ahead of `main`; diff shows deletions relative to current `main`. | `.idea`, `services/tailscale_remote_access_architecture.md` | Medium | Needs review | Confirm whether branch is stale after PR #71 merge. | Branch is 3 commits behind `main`, 0 ahead. |
| `docker-consolidation` | `main` | No commits ahead of `main`; diff shows deletions relative to current `main`. | `.idea`, `services/tailscale_remote_access_architecture.md` | Medium | Needs review | Confirm whether branch is stale after PR #71 merge. | Branch is 2 commits behind `main`, 0 ahead. |
| `enable-websearch` | `main` | No commits ahead of `main`; diff shows deleted procedure/service docs and Obsidian workspace changes. | `.obsidian/workspace.json`, `.idea`, `procedures/prometheus_ollama_model_management_procedure.md`, `services/tailscale_remote_access_architecture.md` | High | Needs review | Validate whether deleted documentation was superseded before considering merge. | Branch is 4 commits behind `main`, 0 ahead. |
| `initialize-openwebui` | `main` | No commits ahead of `main`; diff shows deleted ingress/reverse-proxy docs plus modified Prometheus docs. | `.github/ISSUE_TEMPLATE`, `.gitignore`, `.obsidian`, `Architecture`, `procedures`, `services`, `systems/prometheus-ubuntu.md` | High | Needs review | Validate against merged PR #60 and later reverse-proxy PRs before reuse. | Branch is 11 commits behind `main`, 0 ahead. |
| `initialize-prometheus` | `main` | Four commits ahead with Prometheus initialization docs, compute architecture, and NVIDIA runtime ADR; also deletes several current docs. | `Architecture/compute-architecture.md`, `decisions/ADR-006-Prometheus-Container-Runtime-and-NVIDIA-GPU-Enablemented.md`, `procedures/prometheus-initialization.md`, `procedures/prometheus-nfs-mounts.md`, `procedures/prometheus-nvidia-runtime.md`, deleted reverse-proxy docs | High | Potentially mergeable after selective validation | Review added Prometheus docs without accepting deletions or weakening current ingress docs. | Branch is 9 commits behind `main`, 4 ahead. |
| `refactor-to-template` | `main` | No commits ahead of `main`; diff shows `.gitignore`/Obsidian workspace changes and deleted docs. | `.gitignore`, `.obsidian/workspace.json`, `.idea`, `procedures/prometheus_ollama_model_management_procedure.md`, `services/tailscale_remote_access_architecture.md` | High | Needs review | Confirm whether branch is stale and whether any template work exists outside diff. | Branch is 5 commits behind `main`, 0 ahead. |

## Known Branches

- `add_modify_llm_models`
- `docker-consolidation`
- `enable-websearch`
- `initialize-openwebui`
- `initialize-prometheus`
- `refactor-to-template`

## Suggested Validation Order

1. Documentation/template normalization branches
2. Infrastructure documentation branches
3. Service-specific branches
4. Docker/runtime branches
5. Experimental AI/model branches

## Follow-Up Issues

| Issue | Branch | Purpose | Status |
|---|---|---|---|
| Needs validation | `initialize-prometheus` | Review Prometheus initialization, NFS mount, NVIDIA runtime, and compute architecture docs for selective migration. | Not created |
| Needs validation | `enable-websearch` | Determine whether SearXNG/web search work exists and whether issue #72 covers it. | Not created |
| Needs validation | `refactor-to-template` | Determine whether template work is stale or superseded by current working tree templates. | Not created |
