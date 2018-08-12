import sys
import logging
from psycopg2.extras import Json
from pymq import PyMQ
from pymq.queue.postgres import PostgresQueue
from pymq.command import MQCommandEngine
from examples.command_postgres import database


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
log = logging.getLogger(__name__)


INSERT_STATEMENT = (
    "INSERT INTO mq.message(message_id, command, payload) "
    "VALUES (:message_id, :command, :payload)"
)

messages = [
    {'message_id': 'mid_1', 'command': 'cmd1', 'payload': Json({'foo': 1})},
    {'message_id': 'mid_2', 'command': 'cmd2', 'payload': Json({'foo': 2})},
]


with database.start_transaction() as session:
    session.execute(INSERT_STATEMENT, messages)


postgres_queue = PostgresQueue(database.db_engine)
queue = PyMQ(postgres_queue)
cmd_engine = MQCommandEngine(queue)


""" Handle queue edge cases """


@cmd_engine.get_command
def get_command(msg):
    return msg['command']


@cmd_engine.fail_handler
def fail_handler(ctx, cmd, msg, error):
    log.info(f'Handler for {cmd} failed with error: {error}')
    raise error  # raising here will crash the queue


@cmd_engine.no_message
def no_message(ctx):
    log.info('No message found, exiting')
    sys.exit(1)


@cmd_engine.no_handler
def no_handler(ctx, cmd, msg):
    log.info(f'No handler for {cmd}')


""" Handle messages """


@cmd_engine.handles('cmd1')
def handle_cmd1(ctx, cmd, msg):
    logging.info(f'received command: {cmd}')
    log.info(f'full message: {msg}')


has_failed = False


@cmd_engine.handles('cmd2')
def handle_cmd2(ctx, cmd, msg):
    global has_failed
    log.info(f'received command: {cmd}')
    log.info(f'full message: {msg}')
    if not has_failed:
        log.info('failing on the first try')
        has_failed = True
        raise Exception('oh no')
    log.info('succeeding on the second try')


cmd_engine.start()
