from datetime import timedelta

from celery import Celery

celery_app = Celery(
    "coffee_shop",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
    include=["app.workers.tasks.user_cleanup"]
)

celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "delete_unverified_users_daily": {
        "task": "app.workers.tasks.user_cleanup.delete_unverified_users",
        "schedule": timedelta(days=1),
    },
}
