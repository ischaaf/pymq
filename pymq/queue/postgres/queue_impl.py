import datetime
from pymq.queue import BaseQueue
from sqlalchemy.orm import Session
from sqlalchemy.exc import ResourceClosedError


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
        self.has_saved = False

    def save(self):
        if self.has_saved:
            raise Exception('already saved')
        self.session.execute("SAVEPOINT mq_message_deleted")
        self.has_saved = True

    def rollback_to_save(self):
        if not self.has_saved:
            raise Exception('no save')
        self.session.execute("ROLLBACK TO SAVEPOINT mq_message_deleted")
        self.has_saved = False

    def commit(self):
        self.session.commit()
        self.session.close()
        self.conn.close()

    def rollback(self):
        self.session.rollback()
        self.session.close()
        self.conn.close()


class PostgresQueue(BaseQueue):
    def __init__(self, db_engine):
        self._engine = db_engine

    def get_context(self):
        conn = self._engine.connect()
        session = Session(conn)
        ctx = PostgresContext(conn, session)
        return ctx

    def dequeue(self, ctx):
        response = ctx.session.execute(DEQUEUE_SQL)
        if response.rowcount == 0:
            return None
        message = dump_message(response.fetchone())
        ctx.save()
        return message

    def no_message(self, ctx):
        ctx.commit()
        return None

    def message_success(self, ctx, message):
        try:
            ctx.commit()
        except ResourceClosedError as e:
            pass
        return True

    def message_fail(self, ctx, message, error):
        try:
            ctx.rollback()
        except ResourceClosedError as e:
            pass
        raise error
