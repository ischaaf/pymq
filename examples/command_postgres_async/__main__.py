"""
Each message will still receive it's own database connection
and transaction.
AsyncPostgresQueue reserves one connection for handling
notifications from the db. Therefore the db engine should
have at least (max_messages + 1) connections
"""


import sys
import logging
from psycopg2.extras import Json

import asyncio
# Import Async versions of the PyMQ stack

# Provides the generator queue interface
from pymq import AsyncPyMQ

# Provides the queue implementation
from pymq.queue.postgres import AsyncPostgresQueue

# Provides the command pattern structure
from pymq.command import AsyncMQCommandEngine

from examples.command_postgres_async import database


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
log = logging.getLogger(__name__)


CLEAR_QUEUE = "TRUNCATE TABLE mq.message"
INSERT_STATEMENT = (
    "INSERT INTO mq.message(message_id, command, payload) "
    "VALUES (:message_id, :command, :payload)"
)

messages = [
    {'message_id': 'mid_1', 'command': 'cmd1', 'payload': Json({'foo': 1})},
    {'message_id': 'mid_2', 'command': 'cmd2', 'payload': Json({'foo': 2})},
]
channel = 'mq_new_message'


with database.start_transaction() as session:
    session.execute(CLEAR_QUEUE)
    session.execute(INSERT_STATEMENT, messages)


postgres_queue = AsyncPostgresQueue(
    database.db_engine,
    channel,
    asyncio.get_event_loop()
)
queue = AsyncPyMQ(postgres_queue)
cmd_engine = AsyncMQCommandEngine(
    queue,
    asyncio.get_event_loop(),
    max_messages=5
)


""" Handle queue edge cases """


@cmd_engine.get_command
def get_command(msg):
    return msg['command']


@cmd_engine.fail_handler
def fail_handler(ctx, cmd, msg, error):
    log.info(f'Handler for {cmd} failed with error: {error}')
    # raise error  # raising here will crash the queue


@cmd_engine.no_message
def no_message(ctx):
    log.info('No message found, exiting')
    sys.exit(1)


@cmd_engine.no_handler
def no_handler(ctx, cmd, msg):
    log.info(f'No handler for {cmd}')


""" Handle messages """


@cmd_engine.handles('cmd1')
async def handle_cmd1(ctx, cmd, msg):
    log.info(f'received command: {cmd}, sleeping before processing')
    await asyncio.sleep(5)
    log.info(f'full message: {msg}')


has_failed = False


@cmd_engine.handles('cmd2')
async def handle_cmd2(ctx, cmd, msg):
    global has_failed
    log.info(f'received command: {cmd}')
    log.info(f'full message: {msg}')
    if not has_failed:
        log.info('failing on the first try')
        has_failed = True
        raise Exception('oh no')
    log.info('succeeding on the second try')

loop = asyncio.get_event_loop()
loop.create_task(cmd_engine.start())
loop.run_forever()
