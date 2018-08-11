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
qcmd = MQCommandEngine(queue)


""" Handle queue edge cases """


@qcmd.get_command
def get_command(msg):
    return msg['command']


@qcmd.fail_handler
def fail_handler(ctx, cmd, msg, error):
    print(f'Handler for {cmd} failed with error: {error}')


@qcmd.no_message
def no_message(ctx):
    print('No message found, exiting')
    sys.exit(1)


@qcmd.no_handler
def no_handler(ctx, cmd, msg):
    print(f'No handler for {cmd}')


""" Handle messages """


@qcmd.handles('cmd1')
def handle_cmd1(ctx, cmd, msg):
    print(f'received command: {cmd}')
    print(f'full message: {msg}')


has_failed = False


@qcmd.handles('cmd2')
def handle_cmd2(ctx, cmd, msg):
    global has_failed
    print(f'received command: {cmd}')
    print(f'full message: {msg}')
    if not has_failed:
        print('failing on the first try')
        has_failed = True
        raise Exception('oh no')
    print('succeeding on the second try')


qcmd.start()
