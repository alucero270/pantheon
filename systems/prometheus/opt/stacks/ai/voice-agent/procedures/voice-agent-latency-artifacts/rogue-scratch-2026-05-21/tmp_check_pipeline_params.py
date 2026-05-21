import inspect
from pipecat.pipeline.task import PipelineParams
src = inspect.getsource(PipelineParams.__init__)
print(src)
