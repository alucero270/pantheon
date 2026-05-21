from pipecat.observers.user_bot_latency_observer import UserBotLatencyObserver
import inspect
src = inspect.getsource(UserBotLatencyObserver.__init__)
print(src)
print('---')
src2 = inspect.getsource(UserBotLatencyObserver.event_handler)
print(src2)
