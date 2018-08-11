from psycopg2.extras import Json
from pymq import PyMQ
from pymq.queue.postgres import PostgresQueue

from examples.pymq_postgres import database


INSERT_STATEMENT = (
    "INSERT INTO mq.message(message_id, command, payload) "
    "VALUES (:message_id, :command, :payload)"
)

messages = [
    {'message_id': 'mid_1', 'command': 'test.command', 'payload': Json({'foo': 1})},
    {'message_id': 'mid_2', 'command': 'test.command', 'payload': Json({'foo': 2})},
]


with database.start_transaction() as session:
    session.execute(INSERT_STATEMENT, messages)


def main():
    # Construct a queue implementation from a postgres engine
    postgres_queue = PostgresQueue(database.db_engine)

    # construct the queue
    queue = PyMQ(postgres_queue)

    # get the first message
    with queue.dequeue() as (ctx, msg):
        print(f'got message: {msg}')

    try:
        with queue.dequeue() as (ctx, msg):
            print(f'got message: {msg}')
            raise Exception('oh no')
    except Exception as e:
        print('exception while handling message!')

    with queue.dequeue() as (ctx, msg):
        print(f'got message: {msg}')
    with queue.dequeue() as (ctx, msg):
        print(f'got message: {msg}')


main()
