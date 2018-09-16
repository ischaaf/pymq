import datetime
import select
from pymq.queue import BaseQueue
from sqlalchemy.orm import Session


DEQUEUE_SQL = """
   DELETE FROM mq.message
    WHERE id = (
          SELECT id
            FROM mq.message
           WHERE process_on <= now()
           ORDER BY id ASC
             FOR UPDATE SKIP LOCKED
           LIMIT 1
          )
RETURNING *;
"""


def dump_message(message):
    result = dict(message)
    for key, value in result.items():
        if isinstance(value, datetime.datetime):
            result[key] = value.isoformat()
    return result


class PostgresContext(object):
    def __init__(self, conn, session):
        self.conn = conn
        self.session = session

    def commit(self):
        self.session.commit()
        self.session.close()
        self.conn.close()

    def rollback(self):
        self.session.rollback()
        self.session.close()
        self.conn.close()


class PostgresQueue(BaseQueue):
    def __init__(self, db_engine, channel):
        self._engine = db_engine
        self._conn = db_engine.connect()

        cursor = self._conn.connection.cursor()
        cursor.execute(f'LISTEN {channel};')
        self._conn.connection.commit()

    def get_context(self):
        conn = self._engine.connect()
        session = Session(conn)
        ctx = PostgresContext(conn, session)
        return ctx

    def check_for_message(self, ctx):
        response = ctx.session.execute(DEQUEUE_SQL)
        if response.rowcount == 0:
            return None
        message = dump_message(response.fetchone())
        return message

    def poll_for_message(self, ctx, timeout):
        conn = self._conn.connection
        if select.select([conn], [], [], timeout) == ([], [], []):
            return None

        conn.poll()
        conn.notifies = []
        msg = self.check_for_message(ctx)
        return msg

    def dequeue(self, ctx, timeout=30):
        msg = self.check_for_message(ctx)
        if msg:
            return msg
        return self.poll_for_message(ctx, timeout)

    def no_message(self, ctx):
        ctx.commit()
        return None

    def message_success(self, ctx, message):
        ctx.commit()
        return True

    def message_fail(self, ctx, message, error):
        ctx.rollback()
        raise error
