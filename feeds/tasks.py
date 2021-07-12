from django.conf import settings
from rest_framework.exceptions import ValidationError
from celery.exceptions import MaxRetriesExceededError
from celery import shared_task, group

from feeds.models import Feed
from feeds.utils import update_feed, send_failure_notification


@shared_task(max_retries=settings.CELERY_MAX_RETRIES, default_retry_delay=settings.CELERY_RETRY_DELAY)
def feed_update_task(feed_pk):
    feed = Feed.objects.get(pk=feed_pk)
    try:
        result = update_feed(feed)
    except ValidationError:
        result = False

    if result is False:
        try:
            feed_update_task.retry()
        except MaxRetriesExceededError:
            feed.updated = False
            feed.save()
            send_failure_notification(feed)


@shared_task
def update_feeds_task():
    feeds_pks = Feed.objects.filter(updated=True).values_list('id', flat=True)
    tasks = [feed_update_task.s(feed_pk) for feed_pk in feeds_pks]
    group(tasks).apply_async()
