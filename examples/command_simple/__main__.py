import sys
from pymq import PyMQ
from pymq.queue.memory import MemoryQueue
from pymq.command import MQCommandEngine


messages = [
    {'command': 'cmd1', 'payload': 'message 1'},
    {'command': 'cmd2', 'payload': 'message 2'},
]


mem_queue = MemoryQueue(messages)
queue = PyMQ(mem_queue)
cmd_engine = MQCommandEngine(queue)


""" Handle queue edge cases """


@cmd_engine.get_command
def get_command(msg):
    return msg['command']


@cmd_engine.fail_handler
def fail_handler(ctx, cmd, msg, error):
    print(f'Handler for {cmd} failed with error: {error}')


@cmd_engine.no_message
def no_message(ctx):
    print('No message found, exiting')
    sys.exit(1)


@cmd_engine.no_handler
def no_handler(ctx, cmd, msg):
    print(f'No handler for {cmd}')


""" Handle messages """


@cmd_engine.handles('cmd1')
def handle_cmd1(ctx, cmd, msg):
    print(f'received command: {cmd}')
    print(f'full message: {msg}')


has_failed = False


@cmd_engine.handles('cmd2')
def handle_cmd2(ctx, cmd, msg):
    global has_failed
    print(f'received command: {cmd}')
    print(f'full message: {msg}')
    if not has_failed:
        print('failing on the first try')
        has_failed = True
        raise Exception('oh no')
    print('succeeding on the second try')


cmd_engine.start()
