path = '/home/alex/stacks/voice-agent/pipecat-quickstart/pipecat-quickstart/server/bot.py'
with open(path) as f:
    c = f.read()

# Add import
old_imports = 'from loguru import logger'
new_imports = '''from loguru import logger
from pipecat.observers.user_bot_latency_observer import UserBotLatencyObserver'''
c = c.replace(old_imports, new_imports)

# Add observer creation and event handlers after context definition
old_after_context = '''    pipeline = Pipeline(['''
new_after_context = '''    latency_observer = UserBotLatencyObserver()

    @latency_observer.event_handler("on_latency_measured")
    async def on_latency_measured(observer, latency):
        logger.info(f"User-to-bot latency: {latency:.3f}s")

    @latency_observer.event_handler("on_latency_breakdown")
    async def on_latency_breakdown(observer, breakdown):
        logger.info("Latency breakdown:")
        for event in breakdown.chronological_events():
            logger.info(f"  {event}")

    pipeline = Pipeline(['''
c = c.replace(old_after_context, new_after_context)

# Add observer to PipelineParams
old_params = '''PipelineParams(enable_metrics=True, enable_usage_metrics=True)'''
new_params = '''PipelineParams(observers=[latency_observer], enable_metrics=True, enable_usage_metrics=True)'''
c = c.replace(old_params, new_params)

with open(path, 'w') as f:
    f.write(c)

print("Changes applied")

# Verify
with open(path) as f:
    for i, line in enumerate(f, 1):
        if 'latency_observer' in line or 'LatencyObserver' in line or 'on_latency' in line:
            print(f'{i}: {line.rstrip()}')
