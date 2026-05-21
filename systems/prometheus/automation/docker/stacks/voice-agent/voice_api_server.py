"""Local OpenAI-compatible voice API for Pantheon voice-agent validation.

This server intentionally uses the public Qwen3-TTS and Transformers APIs.
Do not patch qwen_tts files in site-packages as part of the baseline path.
"""

from __future__ import annotations

import io
import logging
import os
import time
from typing import Any

import numpy as np
import soundfile as sf
import torch
import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("voice_api")

app = FastAPI(title="Pantheon Local Voice API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("VOICE_API_CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


QWEN3_TTS_PATH = os.getenv(
    "QWEN3_TTS_PATH",
    "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice",
)
WHISPER_PATH = os.getenv(
    "WHISPER_PATH",
    "/mnt/local/nvme/ai/models/stt/whisper/large-v3-turbo",
)
QWEN_SPEAKER = os.getenv("QWEN_SPEAKER", "Ryan")
QWEN_LANGUAGE = os.getenv("QWEN_LANGUAGE", "English")
QWEN_TTS_BACKEND = os.getenv("QWEN_TTS_BACKEND", "hybrid").strip().lower()
QWEN_PREWARM_TEXT = os.getenv("QWEN_PREWARM_TEXT", "OK.").strip()
VOICE_API_HOST = os.getenv("VOICE_API_HOST", "127.0.0.1")
VOICE_API_PORT = int(os.getenv("VOICE_API_PORT", "8002"))
VOICE_API_DEVICE = os.getenv(
    "VOICE_API_DEVICE",
    "cuda:0" if torch.cuda.is_available() else "cpu",
)
VOICE_API_DTYPE = os.getenv("VOICE_API_DTYPE", "bfloat16")
QWEN_ATTN_IMPLEMENTATION = os.getenv("QWEN_ATTN_IMPLEMENTATION", "").strip()

tts_model = None
stt_processor = None
stt_model = None
startup_seconds: float | None = None


class TTSRequest(BaseModel):
    model: str = "tts-1"
    input: str = Field(min_length=1)
    voice: str = "alloy"
    response_format: str = "wav"
    speed: float = Field(default=1.0, ge=0.25, le=4.0)
    non_streaming_mode: bool | None = None
    max_new_tokens: int | None = None
    temperature: float | None = None
    top_k: int | None = None
    top_p: float | None = None


def _dtype_from_env() -> torch.dtype:
    if VOICE_API_DTYPE == "float16":
        return torch.float16
    if VOICE_API_DTYPE == "float32":
        return torch.float32
    return torch.bfloat16


def _triton_dtype_from_env() -> str:
    if VOICE_API_DTYPE == "float16":
        return "fp16"
    if VOICE_API_DTYPE == "float32":
        return "fp32"
    return "bf16"


def _triton_device_from_env() -> str:
    if VOICE_API_DEVICE.startswith("cuda"):
        return "cuda"
    return VOICE_API_DEVICE


def _timed(label: str, start: float) -> float:
    elapsed = time.perf_counter() - start
    logger.info("%s_seconds=%.3f", label, elapsed)
    return elapsed


def _content_type(fmt: str) -> str:
    return {
        "wav": "audio/wav",
        "mp3": "audio/mpeg",
        "opus": "audio/opus",
        "flac": "audio/flac",
        "aac": "audio/aac",
        "pcm": "audio/L16; rate=24000; channels=1",
    }.get(fmt, "audio/wav")


def _tts_response(audio_array: np.ndarray, sample_rate: int, fmt: str) -> Response:
    fmt = fmt.lower()
    if fmt == "pcm":
        raw = np.clip(audio_array, -1.0, 1.0)
        raw = (raw * 32767).astype(np.int16).tobytes()
        return Response(content=raw, media_type=_content_type(fmt))

    write_format = {
        "wav": "wav",
        "mp3": "mp3",
        "opus": "opus",
        "flac": "flac",
        "aac": "aac",
    }.get(fmt, "wav")
    buf = io.BytesIO()
    sf.write(buf, audio_array, sample_rate, format=write_format)
    buf.seek(0)
    return Response(content=buf.read(), media_type=_content_type(fmt))


def _apply_speed(audio_array: np.ndarray, speed: float) -> np.ndarray:
    if abs(speed - 1.0) < 0.01:
        return audio_array

    import librosa

    stretched = librosa.effects.time_stretch(audio_array.astype(np.float32), rate=speed)
    return stretched.astype(np.float32)


def _load_audio(audio_bytes: bytes) -> tuple[np.ndarray, int]:
    try:
        data, sample_rate = sf.read(io.BytesIO(audio_bytes))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read audio: {exc}") from exc

    if data.ndim > 1:
        data = data.mean(axis=1)

    if sample_rate != 16000:
        import librosa

        data = librosa.resample(data, orig_sr=sample_rate, target_sr=16000)
        sample_rate = 16000

    return data.astype(np.float32), sample_rate


@app.on_event("startup")
async def load_models() -> None:
    global startup_seconds, stt_model, stt_processor, tts_model
    start = time.perf_counter()
    logger.info(
        "voice_api_device=%s dtype=%s qwen_tts_backend=%s",
        VOICE_API_DEVICE,
        VOICE_API_DTYPE,
        QWEN_TTS_BACKEND,
    )

    load_start = time.perf_counter()
    logger.info("loading_qwen3_tts=%s", QWEN3_TTS_PATH)
    if QWEN_TTS_BACKEND in {"hybrid", "triton_hybrid"}:
        from qwen3_tts_triton import TritonFasterRunner

        tts_model = TritonFasterRunner(
            model_id=QWEN3_TTS_PATH,
            device=_triton_device_from_env(),
            dtype=_triton_dtype_from_env(),
        )
        tts_model.load_model()
        _timed("qwen3_tts_hybrid_load", load_start)
        if QWEN_PREWARM_TEXT:
            warm_start = time.perf_counter()
            logger.info("prewarming_qwen3_tts_hybrid chars=%s", len(QWEN_PREWARM_TEXT))
            with torch.inference_mode():
                tts_model.generate(
                    text=QWEN_PREWARM_TEXT,
                    language=QWEN_LANGUAGE,
                    speaker=QWEN_SPEAKER,
                    max_new_tokens=256,
                )
            _timed("qwen3_tts_hybrid_prewarm", warm_start)
    elif QWEN_TTS_BACKEND in {"qwen", "stock"}:
        from qwen_tts import Qwen3TTSModel

        qwen_kwargs: dict[str, Any] = {
            "device_map": VOICE_API_DEVICE,
            "dtype": _dtype_from_env(),
        }
        if QWEN_ATTN_IMPLEMENTATION:
            qwen_kwargs["attn_implementation"] = QWEN_ATTN_IMPLEMENTATION

        tts_model = Qwen3TTSModel.from_pretrained(QWEN3_TTS_PATH, **qwen_kwargs)
        _timed("qwen3_tts_stock_load", load_start)
    else:
        raise RuntimeError(f"Unsupported QWEN_TTS_BACKEND={QWEN_TTS_BACKEND!r}")

    from transformers import WhisperForConditionalGeneration, WhisperProcessor

    load_start = time.perf_counter()
    logger.info("loading_whisper=%s", WHISPER_PATH)
    stt_processor = WhisperProcessor.from_pretrained(WHISPER_PATH)
    stt_model = WhisperForConditionalGeneration.from_pretrained(WHISPER_PATH)
    stt_model.to(VOICE_API_DEVICE)
    stt_model.config.forced_decoder_ids = None
    stt_model.eval()
    _timed("whisper_load", load_start)

    startup_seconds = _timed("voice_api_startup", start)


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse(
        {
            "ok": tts_model is not None and stt_model is not None,
            "device": VOICE_API_DEVICE,
            "dtype": VOICE_API_DTYPE,
            "qwen_tts_backend": QWEN_TTS_BACKEND,
            "qwen_attn_implementation": QWEN_ATTN_IMPLEMENTATION or None,
            "qwen_speaker": QWEN_SPEAKER,
            "startup_seconds": startup_seconds,
        }
    )


def _qwen_generation_kwargs(req: TTSRequest) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if req.non_streaming_mode is not None:
        kwargs["non_streaming_mode"] = req.non_streaming_mode
    if req.max_new_tokens is not None:
        kwargs["max_new_tokens"] = req.max_new_tokens
    if req.temperature is not None:
        kwargs["temperature"] = req.temperature
    if req.top_k is not None:
        kwargs["top_k"] = req.top_k
    if req.top_p is not None:
        kwargs["top_p"] = req.top_p
    return kwargs


def _hybrid_generation_kwargs(req: TTSRequest) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if req.max_new_tokens is not None:
        kwargs["max_new_tokens"] = req.max_new_tokens
    if req.temperature is not None:
        kwargs["temperature"] = req.temperature
    if req.top_k is not None:
        kwargs["top_k"] = req.top_k
    return kwargs


@app.post("/v1/audio/speech")
async def text_to_speech(req: TTSRequest) -> Response:
    if tts_model is None:
        raise HTTPException(status_code=503, detail="TTS model not loaded")

    start = time.perf_counter()
    logger.info("tts_request chars=%s voice=%s format=%s", len(req.input), req.voice, req.response_format)

    try:
        with torch.inference_mode():
            if QWEN_TTS_BACKEND in {"hybrid", "triton_hybrid"}:
                result = tts_model.generate(
                    text=req.input,
                    language=QWEN_LANGUAGE,
                    speaker=QWEN_SPEAKER,
                    **_hybrid_generation_kwargs(req),
                )
            else:
                result = tts_model.generate_custom_voice(
                    text=req.input,
                    language=QWEN_LANGUAGE,
                    speaker=QWEN_SPEAKER,
                    **_qwen_generation_kwargs(req),
                )
    except Exception as exc:
        logger.exception("tts_error")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if isinstance(result, dict):
        if "audio" not in result:
            raise HTTPException(status_code=500, detail="No audio generated")
        audio_array = np.asarray(result["audio"])
        sample_rate = int(result.get("sample_rate") or 24000)
    elif isinstance(result, tuple) and len(result) == 2:
        wavs, sample_rate = result
        if len(wavs) == 0:
            raise HTTPException(status_code=500, detail="No audio generated")
        audio_array = np.asarray(wavs[0])
    else:
        audio_array = np.asarray(result)
        sample_rate = 24000

    generation_seconds = _timed("tts_generation", start)
    audio_array = _apply_speed(audio_array, req.speed)
    response = _tts_response(audio_array, sample_rate, req.response_format)
    response.headers["X-Voice-Generation-Seconds"] = f"{generation_seconds:.3f}"
    response.headers["X-Voice-Speed"] = f"{req.speed:.2f}"
    response.headers["X-Voice-Sample-Rate"] = str(sample_rate)
    response.headers["X-Voice-Bytes"] = str(len(response.body))
    return response


app.add_api_route("/audio/speech", text_to_speech, methods=["POST"])


@app.post("/v1/audio/transcriptions")
async def speech_to_text(
    file: UploadFile = File(...),
    model: str = Form("whisper-1"),
    language: str | None = Form(None),
    response_format: str = Form("json"),
    temperature: float = Form(0.0),
) -> JSONResponse:
    if stt_model is None or stt_processor is None:
        raise HTTPException(status_code=503, detail="STT model not loaded")

    start = time.perf_counter()
    logger.info("stt_request filename=%s model=%s", file.filename, model)

    audio_bytes = await file.read()
    audio_np, sample_rate = _load_audio(audio_bytes)
    input_features = stt_processor(audio_np, sampling_rate=sample_rate, return_tensors="pt").input_features
    input_features = input_features.to(VOICE_API_DEVICE)

    generate_kwargs = {"language": language} if language else {}
    try:
        with torch.inference_mode():
            predicted_ids = stt_model.generate(input_features, **generate_kwargs)
        transcription = stt_processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
    except Exception as exc:
        logger.exception("stt_error")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    elapsed = _timed("stt_generation", start)
    return JSONResponse({"text": transcription, "seconds": round(elapsed, 3)})


app.add_api_route("/audio/transcriptions", speech_to_text, methods=["POST"])


if __name__ == "__main__":
    uvicorn.run(app, host=VOICE_API_HOST, port=VOICE_API_PORT)
