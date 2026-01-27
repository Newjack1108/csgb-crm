"""
RQ Worker for background jobs.
Run with: python -m app.worker
Or: rq worker default
"""
import os
import sys

# Ensure we can import app modules
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from redis import Redis
from rq import Worker, Queue, Connection
from app.core.config import settings

# Listen on the default queue
listen = ['default']

redis_conn = Redis.from_url(settings.REDIS_URL)

if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(listen)
        worker.work()
