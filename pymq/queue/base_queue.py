class BaseQueue(object):
    def get_context(self):
        raise Exception('not implemented')

    def dequeue(self, context):
        raise Exception('not implemented')

    def no_message(self, context):
        return None

    def message_success(self, context, message):
        return True

    def message_fail(self, context, message, error):
        raise error
