import logging
from pymq.command.dispatcher import Dispatcher


log = logging.getLogger(__name__)


def default_fail_handler(ctx, cmd, msg, error):
    raise error


def default_no_message(ctx):
    log.warn('no messages found')


def default_no_handler(ctx, cmd, msg, error):
    log.warn(f'no handler found for command: {cmd}')


def default_get_command(msg):
    if 'command' not in msg:
        raise Exception('Invalid message structure, missing key "command"')
    return msg['command']


class MQCommandEngine(object):
    def __init__(self, engine, dispatcher=Dispatcher()):
        self._engine = engine
        self._base_dispatcher = dispatcher
        self._fail_handler = default_fail_handler
        self._no_handler = default_no_handler
        self._no_message = default_no_message
        self._get_command = default_get_command
        self._dispatchers = []

    def register(self, dispatcher):
        self._dispatchers.append(dispatcher)

    def handles(self, matcher):
        def wrapper_fn(fn):
            self._base_dispatcher.add_handler(matcher, fn)
            return fn
        return wrapper_fn

    def fail_handler(self, fn):
        self._fail_handler = fn
        return fn

    def no_message(self, fn):
        self._no_message = fn
        return fn

    def no_handler(self, fn):
        self._no_handler = fn
        return fn

    def get_command(self, fn):
        self._get_command = fn
        return fn

    def get_handler(self, command):
        handler = self._base_dispatcher.match(command)
        if handler:
            return handler
        for dispatcher in self._dispatchers:
            handler = dispatcher.match(command)
            if handler:
                return handler

    def start(self):
        while True:
            self.handle_next_message()

    def handle_next_message(self):
        with self._engine.dequeue() as (ctx, msg):
            if not msg:
                self._no_message(ctx)
                return
            cmd = self._get_command(msg)
            handler = self.get_handler(cmd)
            if not handler:
                self._no_handler(ctx, cmd, msg)
                return
            try:
                handler(ctx, cmd, msg)
            except Exception as e:
                self._fail_handler(ctx, cmd, msg, e)
