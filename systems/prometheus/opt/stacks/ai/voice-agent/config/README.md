# Voice Agent Config

## Purpose

This folder tracks sanitized Voice Agent runtime config, service launchers, and restore guidance.

## Live Config Candidates

| Live path | Purpose | Git posture |
|---|---|---|
| `/home/alex/stacks/voice-agent/.env` | Local runtime env if present | Do not commit |
| `/home/alex/stacks/voice-agent/.env.example` | Sanitized env example | Git candidate |
| `/home/alex/stacks/voice-agent/voice-api.service` | Candidate systemd unit | Sanitized Git candidate |
| `/home/alex/stacks/voice-agent/voice_api_server.py` | Runtime server implementation | Git candidate if owned by Pantheon |
| `/home/alex/stacks/voice-agent/pipecat-quickstart/pipecat-quickstart/server/bot.py` | Pipecat bot implementation | Git candidate if owned by Pantheon |

## Repository Files

| File | Purpose |
|---|---|
| `.env.example` | Sanitized environment defaults |
| `voice_api_server.py` | Local OpenAI-compatible STT/TTS server |
| `bot.py` | Pipecat validation bot |
| `validate_pipeline.py` | Component latency validation script |
| `voice-api.service` | Candidate systemd unit |
| `start-voice-api.sh` | Minimal local launcher |
| `traefik-voice-agent.yml` | Candidate Traefik dynamic config; not approved for production exposure |
| `compose.yml` | Legacy Speaches scaffold; not current runtime |
| `compose.cuda.yml` | Legacy Speaches GPU override |
| `runtime-baseline.md` | Runtime baseline notes and validation summary |

## Status

This folder is the canonical repository home for sanitized Voice Agent runtime config. Docker-specific automation, if it is revived later, belongs under [[systems/prometheus/automation/docker/stacks/voice-agent/README]] and must not supersede this config folder without an approved layout decision.

## Rules

- Do not commit API keys, private voice samples, transcripts, recordings, generated user data, or provider tokens.
- Treat Qwen3-TTS/STT model paths as local runtime references, not portable config by themselves.
