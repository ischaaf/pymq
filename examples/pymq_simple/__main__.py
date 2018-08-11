from pymq import PyMQ
from pymq.queue.memory import MemoryQueue


messages = [
    'message 1',
    'message 2',
]


def main():
    # Construct a queue implementation from a python list
    mem_queue = MemoryQueue(messages)

    # construct the queue
    queue = PyMQ(mem_queue)

    print(f'The length of the queue is {len(messages)}')  # 2

    # get the first message
    with queue.dequeue() as (ctx, msg):
        print(f'got message: {msg}')
    print(f'The length of the queue is {len(messages)}')  # 1

    try:
        with queue.dequeue() as (ctx, msg):
            print(f'got message: {msg}')
            raise Exception('oh no')
    except Exception as e:
        print('exception while handling message!')
    print(f'The length of the queue is {len(messages)}')  # 1

    with queue.dequeue() as (ctx, msg):
        print(f'got message: {msg}')
    print(f'The length of the queue is {len(messages)}')  # 0
    with queue.dequeue() as (ctx, msg):
        print(f'got message: {msg}')


main()
