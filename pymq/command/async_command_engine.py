from .command_engine import MQCommandEngine
from pymq.command.dispatcher import Dispatcher


class AsyncMQCommandEngine(MQCommandEngine):
    def __init__(self, engine, loop, max_messages, dispatcher=Dispatcher()):
        super(AsyncMQCommandEngine, self).__init__(engine, dispatcher)
        self._loop = loop
        self._max_in_flight = max_messages

    async def start(self):
        for _ in range(self._max_in_flight):
            print('spawning task')
            coro = self.handle_and_track()
            self._loop.create_task(coro)

    async def handle_and_track(self):
        try:
            await self.handle_next_message()
        finally:
            self._loop.create_task(self.handle_and_track())

    async def handle_next_message(self):
        async with self._engine.dequeue() as (ctx, msg):
            if not msg:
                self._no_message(ctx)
                return
            cmd = self._get_command(msg)
            handler = self.get_handler(cmd)
            if not handler:
                self._no_handler(ctx, cmd, msg)
                return
            try:
                await handler(ctx, cmd, msg)
            except Exception as e:
                self._fail_handler(ctx, cmd, msg, e)
