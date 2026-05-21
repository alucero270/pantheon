import inspect

# LLM settings
import pipecat.services.openai.llm as llm_mod
print("=== OpenAILLMService.Settings ===")
sig = inspect.signature(llm_mod.OpenAILLMService.Settings.__init__)
for name, param in sig.parameters.items():
    if name == 'self': continue
    default = param.default if param.default is not inspect.Parameter.empty else 'required'
    print(f"  {name}: {default}")

# PipelineParams
import pipecat.pipeline.task as task_mod
print("\n=== PipelineParams ===")
sig = inspect.signature(task_mod.PipelineParams.__init__)
for name, param in sig.parameters.items():
    if name == 'self': continue
    default = param.default if param.default is not inspect.Parameter.empty else 'required'
    print(f"  {name}: {default}")

# VAD
import pipecat.audio.vad.silero as vad_mod
print("\n=== SileroVADAnalyzer ===")
sig = inspect.signature(vad_mod.SileroVADAnalyzer.__init__)
for name, param in sig.parameters.items():
    if name == 'self': continue
    default = param.default if param.default is not inspect.Parameter.empty else 'required'
    print(f"  {name}: {default}")

# LLMUserAggregatorParams
import pipecat.processors.aggregators.llm_response_universal as agg_mod
print("\n=== LLMUserAggregatorParams ===")
sig = inspect.signature(agg_mod.LLMUserAggregatorParams.__init__)
for name, param in sig.parameters.items():
    if name == 'self': continue
    default = param.default if param.default is not inspect.Parameter.empty else 'required'
    print(f"  {name}: {default}")

# TTS settings (base class)
import pipecat.services.tts_service as tts_mod
print("\n=== TTSService base settings ===")
sig = inspect.signature(tts_mod.TTSService.__init__)
for name, param in sig.parameters.items():
    if name == 'self': continue
    default = param.default if param.default is not inspect.Parameter.empty else 'required'
    print(f"  {name}: {default}")

# OpenAITTSService specific settings
import pipecat.services.openai.tts as openai_tts
print("\n=== OpenAITTSService.Settings ===")
sig = inspect.signature(openai_tts.OpenAITTSService.Settings.__init__)
for name, param in sig.parameters.items():
    if name == 'self': continue
    default = param.default if param.default is not inspect.Parameter.empty else 'required'
    print(f"  {name}: {default}")
