from extras import try_import
from pymq.queue.base_queue import BaseQueue
from pymq.queue import memory

__all__ = [BaseQueue, memory]

# add postgres is sqlalchemy is installed
postgres = try_import('pymq.queue.postgres')
if not postgres:
    del postgres
else:
    __all__.append(postgres)
