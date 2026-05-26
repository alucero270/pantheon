#!/usr/bin/env bash
set -euo pipefail

cd /home/alex/stacks/voice-agent
exec /home/alex/stacks/voice-agent/venv/bin/python3 /home/alex/stacks/voice-agent/voice_api_server.py
