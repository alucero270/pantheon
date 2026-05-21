import io, os, torch, time, numpy as np, soundfile as sf
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn, logging

import qwen_tts.core.models.configuration_qwen3_tts as _qc
_orig_talker_init = _qc.Qwen3TTSTalkerConfig.__init__
_orig_codec_init = _qc.Qwen3TTSTalkerCodePredictorConfig.__init__
_talker_cache = [None]
_codec_cache = [None]
def _patched_talker(self, **kw):
    if _talker_cache[0] is None:
        _orig_talker_init(self, **kw)
        _talker_cache[0] = self.__dict__.copy()
    else:
        self.__dict__.update(_talker_cache[0])
def _patched_codec(self, **kw):
    if _codec_cache[0] is None:
        _orig_codec_init(self, **kw)
        _codec_cache[0] = self.__dict__.copy()
    else:
        self.__dict__.update(_codec_cache[0])
_qc.Qwen3TTSTalkerConfig.__init__ = _patched_talker
_qc.Qwen3TTSTalkerCodePredictorConfig.__init__ = _patched_codec

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voice_api")

app = FastAPI(title="Local Voice API")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

tts_model = None
stt_processor = None
stt_model = None
device = "cuda:0" if torch.cuda.is_available() else "cpu"

QWEN3_TTS_PATH = os.getenv("QWEN3_TTS_PATH", "/mnt/local/nvme/ai/models/TTS/Qwen3-TTS/Qwen3-TTS-12Hz-1.7B-CustomVoice")
WHISPER_PATH = os.getenv("WHISPER_PATH", "/mnt/local/nvme/ai/models/stt/whisper/large-v3-turbo")
QWEN_SPEAKER = "uncle_fu"

class TTSRequest(BaseModel):
    model: str = "tts-1"
    input: str
    voice: str = "alloy"
    response_format: str = "wav"
    speed: float = 1.0

TTS_FORMAT_MAP = {"wav": "wav", "mp3": "mp3", "pcm": "wav", "opus": "opus", "flac": "flac", "aac": "aac"}

def _tts_response(audio_array: np.ndarray, sr: int, fmt: str):
    if fmt == "pcm":
        raw = (audio_array * 32767).astype(np.int16).tobytes()
        return Response(content=raw, media_type="audio/L16; rate=24000; channels=1")
    buf = io.BytesIO()
    write_fmt = TTS_FORMAT_MAP.get(fmt, "wav")
    sf.write(buf, audio_array, sr, format=write_fmt)
    return Response(content=buf.getvalue(), media_type=f"audio/{write_fmt}")

@app.on_event("startup")
async def startup():
    global tts_model, stt_processor, stt_model
    logger.info(f"Loading Qwen3-TTS from {QWEN3_TTS_PATH}")
    from qwen_tts import Qwen3TTSModel
    t0 = time.time()
    tts_model = Qwen3TTSModel.from_pretrained(QWEN3_TTS_PATH, device_map=device, dtype=torch.bfloat16)
    logger.info(f"Qwen3-TTS loaded in {time.time()-t0:.1f}s")
    
    logger.info("Pre-warming TTS model...")
    t0 = time.time()
    _gen_kwargs = {"max_new_tokens": 100}
    wavs, sr = tts_model.generate_custom_voice(
        text="Pre-warm test.",
        language="English",
        speaker=QWEN_SPEAKER,
        **_gen_kwargs,
    )
    logger.info(f"TTS pre-warm complete ({time.time()-t0:.2f}s)")

    logger.info(f"Loading Whisper from {WHISPER_PATH}")
    from transformers import WhisperProcessor, WhisperForConditionalGeneration
    stt_processor = WhisperProcessor.from_pretrained(WHISPER_PATH)
    stt_model = WhisperForConditionalGeneration.from_pretrained(WHISPER_PATH).to(device)
    logger.info("Whisper loaded")

@app.post("/v1/audio/speech")
async def text_to_speech(req: TTSRequest):
    if tts_model is None:
        raise HTTPException(status_code=503, detail="TTS model not loaded")
    logger.info(f"TTS: input={req.input[:50]}... voice={req.voice}")
    _t_start = time.time()

    try:
        wavs, sr = tts_model.generate_custom_voice(
            text=req.input,
            language="English",
            speaker=QWEN_SPEAKER,
            do_sample=True,
            max_new_tokens=200,
        )
        logger.info(f"TTS generate took {time.time()-_t_start:.2f}s for {len(req.input)} chars")
        audio = wavs[0]
        if req.speed != 1.0:
            from scipy import signal
            audio = signal.resample(audio, int(len(audio) / req.speed))
        return _tts_response(audio, sr, req.response_format)
    except Exception as e:
        logger.exception("TTS generation failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/audio/transcriptions")
async def speech_to_text(file: UploadFile = File(...), language: str = Form("english")):
    if stt_model is None:
        raise HTTPException(status_code=503, detail="STT model not loaded")
    audio_bytes = await file.read()
    audio_np, sr = sf.read(io.BytesIO(audio_bytes))
    if sr != 16000:
        from scipy import signal
        audio_np = signal.resample(audio_np, int(len(audio_np) * 16000 / sr))
    input_features = stt_processor(audio_np, sampling_rate=16000, return_tensors="pt").input_features.to(device)
    predicted_ids = stt_model.generate(input_features, language=language)
    text = stt_processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
    return JSONResponse({"text": text})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
