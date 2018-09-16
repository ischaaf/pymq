import asyncio
from sqlalchemy.orm import Session
from .queue_impl import PostgresQueue, PostgresContext


class AsyncPostgresQueue(PostgresQueue):
    def __init__(self, db_engine, channel, loop):
        super(AsyncPostgresQueue, self).__init__(db_engine, channel)
        self._loop = loop

    async def get_context(self):
        conn = await self._loop.run_in_executor(None, self._engine.connect)
        session = Session(conn)
        ctx = PostgresContext(conn, session)
        return ctx

    async def poll_for_message(self, ctx, timeout):
        conn = self._conn.connection

        # create a future to wait for data on the connection socket
        future = asyncio.Future()
        self._loop.add_reader(conn, future.set_result, None)
        future.add_done_callback(lambda f: self._loop.remove_reader(conn))
        await future

        conn.poll()
        conn.notifies = []
        msg = self.check_for_message(ctx)
        return msg

    async def dequeue(self, ctx, timeout=30):
        msg = self.check_for_message(ctx)
        if msg:
            return msg
        return await self.poll_for_message(ctx, timeout)
