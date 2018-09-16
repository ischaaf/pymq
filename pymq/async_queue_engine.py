from contextlib import asynccontextmanager


class AsyncPyMQ(object):
    def __init__(self, queue):
        self._queue = queue

    @asynccontextmanager
    async def dequeue(self):
        context = await self._queue.get_context()
        message = await self._queue.dequeue(context)
        if not message:
            try:
                yield context, message
                return
            except Exception as e:
                raise e
            finally:
                self._queue.no_message(context)
        try:
            yield context, message
            self._queue.message_success(context, message)
        except Exception as e:
            self._queue.message_fail(context, message, e)
            raise e
