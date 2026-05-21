import inspect
from pipecat.services.tts_service import TTSService
src = inspect.getsource(TTSService._maybe_pause_frame_processing)
print(src)
