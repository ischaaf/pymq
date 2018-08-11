class Dispatcher(object):
    def __init__(self, prefix=''):
        self._dispatch_table = dict()
        self._prefix = prefix

    def string_matcher(self, matcher):
        return lambda cmd: cmd == matcher

    def add_handler(self, matcher, handler):
        if not callable(handler):
            raise Exception('handler must be a function')
        self._dispatch_table[matcher] = handler

    def handles(self, matcher):
        def wrapper_fn(fn):
            self.add_handler(matcher, fn)
            return fn
        return wrapper_fn

    def get_matcher(self, matcher):
        if not callable(matcher):
            return self.string_matcher(matcher)
        return matcher

    def match(self, command):
        if self._prefix and not command.startswith(self._prefix):
            return None
        for matcher, handler in self._dispatch_table.items():
            if self.get_matcher(matcher)(command[len(self._prefix):]):
                return handler
        return None
