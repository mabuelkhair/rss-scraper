from unittest import mock

from django.test import TestCase, override_settings
from django.conf import settings

from .factories import FeedFactory
from feeds.tasks import update_feeds_task, feed_update_task
from feeds.models import Feed


class TestFeedUpdatingTasks(TestCase):

    @mock.patch('feeds.tasks.feed_update_task.s')
    def test_update_feeds_marked_for_update(self, task_mock):
        FeedFactory.create_batch(8, updated=True)
        FeedFactory.create_batch(2, updated=False)
        self.assertEqual(Feed.objects.count(), 10)
        update_feeds_task.apply()
        self.assertEqual(task_mock.call_count, 8)

    @mock.patch('feeds.tasks.update_feed', return_value=True)
    @mock.patch('feeds.tasks.feed_update_task.retry')
    @mock.patch('feeds.tasks.send_failure_notification')
    def test_update_feed_task(self, email_mock, retry_task_mock, update_feed_mock):
        feed = FeedFactory.create(updated=True)
        feed_update_task(feed.pk)
        self.assertEqual(retry_task_mock.call_count, 0)
        self.assertEqual(email_mock.call_count, 0)
        self.assertEqual(update_feed_mock.call_count, 1)
        feed.refresh_from_db()
        self.assertTrue(feed.updated)

    @override_settings(task_always_eager=True)
    @mock.patch('feeds.tasks.update_feed', return_value=False)
    @mock.patch('feeds.tasks.send_failure_notification')
    def test_fallback_and_notify_user(self, email_mock, update_feed_mock):
        feed = FeedFactory.create(updated=True)
        feed_update_task.delay(feed.pk)
        # assert it called once + number of retries in settings
        self.assertEqual(update_feed_mock.call_count, settings.CELERY_MAX_RETRIES + 1)
        # only one email notification sent to user
        self.assertEqual(email_mock.call_count, 1)
        feed.refresh_from_db()
        self.assertFalse(feed.updated)
