import sys

from celery import Celery
from app.config import settings

celery_app = Celery(
    "foxhunter",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks"],
)

_worker_conf: dict = {
    "result_expires": 3600,
    "task_serializer": "json",
    "accept_content": ["json"],
    "result_serializer": "json",
    "timezone": "UTC",
    "enable_utc": True,
}
# Windows 默认 prefork 多进程与 billiard 组合易出现
# ``ValueError: not enough values to unpack (expected 3, got 0)``，改用 solo 单进程池。
if sys.platform == "win32":
    _worker_conf["worker_pool"] = "solo"

celery_app.conf.update(_worker_conf)