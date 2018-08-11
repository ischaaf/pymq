from contextlib import contextmanager
import sqlalchemy
from sqlalchemy.orm import Session


db_engine = sqlalchemy.create_engine(
    'postgres://postgres@localhost:5433/postgres',
    pool_size=1,
    max_overflow=0
)


@contextmanager
def start_transaction() -> Session:
    conn = db_engine.connect()
    try:
        session = Session(conn)
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()
        conn.close()
