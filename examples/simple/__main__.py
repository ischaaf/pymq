from pymq import PyMQ
from pymq.queue.memory import MemoryQueue


messages = [
    {'command': 'test.message', 'payload': {'foo': 1}},
    {'command': 'another.message', 'payload': {'foo': 2}},
    {'command': 'v1.create.resource', 'payload': {'foo': 3}},
    {'command': 'v1.delete.resource', 'payload': {'foo': 3}},
]


def main():
    queue = PyMQ(MemoryQueue(messages))
    with queue.next_message() as (ctx, msg):
        print(msg)
        assert msg['payload']['foo'] == 1
    assert len(messages) == 3

    try:
        with queue.next_message() as (ctx, msg):
            print(msg)
            raise Exception('oh no')
    except Exception as e:
        pass
    assert len(messages) == 3

    with queue.next_message() as (ctx, msg):
        print(msg)


main()
