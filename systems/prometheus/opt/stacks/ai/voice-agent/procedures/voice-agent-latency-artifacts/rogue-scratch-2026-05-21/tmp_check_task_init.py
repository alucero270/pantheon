import inspect
from pipecat.pipeline.task import PipelineTask
src = inspect.getsource(PipelineTask.__init__)
print(src)
