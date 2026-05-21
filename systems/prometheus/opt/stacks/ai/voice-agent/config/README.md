# Voice Agent Config

## Purpose

This folder tracks sanitized Voice Agent config notes and restore guidance.

## Live Config Candidates

| Live path | Purpose | Git posture |
|---|---|---|
| `/home/alex/stacks/voice-agent/.env` | Local runtime env if present | Do not commit |
| `/home/alex/stacks/voice-agent/.env.example` | Sanitized env example | Git candidate |
| `/home/alex/stacks/voice-agent/voice-api.service` | Candidate systemd unit | Sanitized Git candidate |
| `/home/alex/stacks/voice-agent/voice_api_server.py` | Runtime server implementation | Git candidate if owned by Pantheon |
| `/home/alex/stacks/voice-agent/pipecat-quickstart/pipecat-quickstart/server/bot.py` | Pipecat bot implementation | Git candidate if owned by Pantheon |

## Status

Sanitized scaffolds exist under [[systems/prometheus/automation/docker/stacks/voice-agent/README]], but canonical config ownership still needs validation.

## Rules

- Do not commit API keys, private voice samples, transcripts, recordings, generated user data, or provider tokens.
- Treat Qwen3-TTS/STT model paths as local runtime references, not portable config by themselves.
