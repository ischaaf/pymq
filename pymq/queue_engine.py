from contextlib import contextmanager


class PyMQ(object):
    def __init__(self, queue):
        self._queue = queue

    @contextmanager
    def dequeue(self):
        context = self._queue.get_context()
        message = self._queue.dequeue(context)
        if not message:
            try:
                yield context, message
            except Exception as e:
                pass
            finally:
                self._queue.no_message(context)
                return
        try:
            yield context, message
            self._queue.message_success(context, message)
        except Exception as e:
            self._queue.message_fail(context, message, e)
