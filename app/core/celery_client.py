import logging
import os

from celery import Celery
from celery.result import AsyncResult

from app.constants import EnvConfig


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CeleryClient:
    _instance = None

    def __new__(cls):
        """Returns the singleton instance or creates a new one if not existend"""
        if cls._instance is None:
            cls._instance = super(CeleryClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Init class variables needed to establish a connection to the database"""
        self._app = Celery(
            "orchestrator",
            broker=os.getenv(EnvConfig.CELERY_BROKER_CONNECTION.value),
            backend=os.getenv(EnvConfig.CELERY_BACKEND_CONNECTION.value),
        )
        self._app.conf.update(
            result_extended=True,
            worker_send_task_events=True,
            task_send_sent_events=True,
        )

    def get_app(self):
        return self._app

    def get_task(self, name: str, queue, *args, **kwargs):
        return self._app.signature(name, queue=queue, *args, **kwargs)

    def get_status(self, task_id: str):
        return AsyncResult(task_id, app=self._app).status

    def get_result(self, task_id: str):
        return AsyncResult(task_id, app=self._app).result
