import asyncio
from psycopg2.extras import Json
from pymq import AsyncPyMQ
from pymq.queue.postgres import AsyncPostgresQueue

from examples.pymq_postgres import database


INSERT_STATEMENT = (
    "INSERT INTO mq.message(message_id, command, payload) "
    "VALUES (:message_id, :command, :payload)"
)

CLEAR_QUEUE = "TRUNCATE TABLE mq.message"

messages = [
    {'message_id': 'mid_1', 'command': 'test.command', 'payload': Json({'foo': 1})},
    {'message_id': 'mid_2', 'command': 'test.command', 'payload': Json({'foo': 2})},
]


with database.start_transaction() as session:
    session.execute(CLEAR_QUEUE)
    session.execute(INSERT_STATEMENT, messages)


channel = 'mq_new_message'


async def main():
    # Construct a queue implementation from a postgres engine
    postgres_queue = AsyncPostgresQueue(
        database.db_engine,
        channel,
        asyncio.get_event_loop()
    )

    # construct the queue
    queue = AsyncPyMQ(postgres_queue)

    # get the first message
    async with queue.dequeue() as (ctx, msg):
        print(f'got message: {msg}')

    try:
        async with queue.dequeue() as (ctx, msg):
            print(f'got message: {msg}')
            raise Exception('oh no')
    except Exception as e:
        print('exception while handling message!')

    async with queue.dequeue() as (ctx, msg):
        print(f'got message: {msg}')

    print('waiting for non-existent message')
    async with queue.dequeue() as (ctx, msg):
        print(f'{msg}')


asyncio.run(main())
