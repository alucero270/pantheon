"""Pipecat bot for Pantheon voice-agent validation.

Run locally on Prometheus with:
    uv run bot.py -t webrtc --host 0.0.0.0 --port 7860
"""

from __future__ import annotations

import os
import json

from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.runner.types import DailyRunnerArguments, RunnerArguments, SmallWebRTCRunnerArguments
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.services.openai.stt import OpenAISTTService
from pipecat.services.openai.tts import OpenAITTSService
from pipecat.transports.base_transport import BaseTransport, TransportParams

try:
    from pipecat.transports.network.small_webrtc import SmallWebRTCTransport
except ImportError:  # Pipecat 1.2.1 compatibility on the installed host.
    from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport


LOCAL_VOICE_API = os.getenv("LOCAL_VOICE_API", "http://127.0.0.1:8002")
LLAMA_SWAP_URL = os.getenv("LLAMA_SWAP_URL", "http://172.17.0.1:8085/v1")
LLAMA_SWAP_KEY = os.getenv("LLAMA_SWAP_KEY", "LOCAL")
LLM_MODEL = os.getenv("VOICE_AGENT_LLM_MODEL", "granite-4.1-8b-gpu")
TTS_VOICE = os.getenv("VOICE_AGENT_TTS_VOICE", "alloy")
TTS_SPEED = float(os.getenv("VOICE_AGENT_TTS_SPEED", "1.5"))
VOICE_AGENT_SYSTEM_PROMPT = os.getenv(
    "VOICE_AGENT_SYSTEM_PROMPT",
    (
        "You are a concise voice assistant for a homelab validation test. "
        "Your response will be spoken aloud. Use one short sentence under twelve words. "
        "Avoid lists, markdown, emojis, and long preambles."
    ),
)
VOICE_AGENT_START_PROMPT = os.getenv("VOICE_AGENT_START_PROMPT", "Greet me in six words.")
VOICE_AGENT_MAX_TOKENS = int(os.getenv("VOICE_AGENT_MAX_TOKENS", "32"))
VOICE_AGENT_TEMPERATURE = float(os.getenv("VOICE_AGENT_TEMPERATURE", "0.4"))
VOICE_AGENT_LLM_EXTRA_JSON = os.getenv("VOICE_AGENT_LLM_EXTRA_JSON", "").strip()


async def run_bot(transport: BaseTransport) -> None:
    logger.info("starting voice-agent bot")
    logger.info("voice_api={} llama_swap={} model={}", LOCAL_VOICE_API, LLAMA_SWAP_URL, LLM_MODEL)

    stt = OpenAISTTService(
        base_url=LOCAL_VOICE_API,
        api_key="not-needed",
        model="whisper-1",
    )

    llm = OpenAILLMService(
        model=LLM_MODEL,
        base_url=LLAMA_SWAP_URL,
        api_key=LLAMA_SWAP_KEY,
        settings=OpenAILLMService.Settings(
            model=LLM_MODEL,
            extra=json.loads(VOICE_AGENT_LLM_EXTRA_JSON) if VOICE_AGENT_LLM_EXTRA_JSON else {},
            system_instruction=VOICE_AGENT_SYSTEM_PROMPT,
            max_tokens=VOICE_AGENT_MAX_TOKENS,
            temperature=VOICE_AGENT_TEMPERATURE,
        ),
    )

    tts = OpenAITTSService(
        base_url=LOCAL_VOICE_API,
        api_key="not-needed",
        voice=TTS_VOICE,
        model="tts-1",
        speed=TTS_SPEED,
    )

    context = LLMContext()
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer()),
    )

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            user_aggregator,
            llm,
            tts,
            transport.output(),
            assistant_aggregator,
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(enable_metrics=True, enable_usage_metrics=True),
    )

    @task.rtvi.event_handler("on_client_ready")
    async def on_client_ready(rtvi):
        logger.info("client ready")
        context.add_message({"role": "user", "content": VOICE_AGENT_START_PROMPT})
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("client connected")

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False)
    await runner.run(task)


async def bot(runner_args: RunnerArguments) -> None:
    if isinstance(runner_args, DailyRunnerArguments):
        from pipecat.transports.daily.transport import DailyParams, DailyTransport

        transport = DailyTransport(
            runner_args.room_url,
            runner_args.token,
            "Pantheon Voice Agent",
            params=DailyParams(audio_in_enabled=True, audio_out_enabled=True),
        )
    elif isinstance(runner_args, SmallWebRTCRunnerArguments):
        transport = SmallWebRTCTransport(
            params=TransportParams(audio_in_enabled=True, audio_out_enabled=True),
            webrtc_connection=runner_args.webrtc_connection,
        )
    else:
        logger.error("unsupported runner arguments type: {}", type(runner_args))
        return

    await run_bot(transport)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
