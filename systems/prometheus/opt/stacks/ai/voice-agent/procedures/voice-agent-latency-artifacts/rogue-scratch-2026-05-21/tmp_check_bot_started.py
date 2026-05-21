import inspect
from pipecat.transports.base_output import BaseOutputTransport
src = inspect.getsource(BaseOutputTransport._bot_started_speaking)
print(src)
