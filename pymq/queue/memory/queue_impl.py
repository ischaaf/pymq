from pymq.queue import BaseQueue


class MemoryQueue(BaseQueue):
    def __init__(self, queue):
        self._queue = queue

    def get_context(self):
        return None

    def dequeue(self, context):
        if len(self._queue) == 0:
            return None
        message = self._queue.pop(0)
        return message

    def message_fail(self, context, message, error):
        self._queue.insert(0, message)
        return False
