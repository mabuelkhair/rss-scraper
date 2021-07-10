from celery.schedules import crontab

tasks = {
    "update_feeds": {
        "task": "feeds.tasks.update_feeds_task",
        "schedule": crontab(minute="*/60"),
    },
}
