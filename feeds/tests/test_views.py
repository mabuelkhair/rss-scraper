import json
from unittest import mock

from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .factories import UserFactory, FeedFactory, ItemFactory
from feeds.models import Feed, Item
from feeds.tests import mocks


class TestFeedViewSet(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.data = {"url": "https://example.com"}

    @mock.patch('feeds.utils.parse_feed', return_value=mocks.valid_feed)
    def test_create_feed(self, feed_mock):
        response = self.client.post(
            '/feeds/',
            data=json.dumps(self.data),
            content_type='application/json'
        )
        json_data = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(feed_mock.call_count, 1)
        self.assertEqual(json_data.get('title'), mocks.valid_feed.feed.title)
        self.assertEqual(json_data.get('link'), mocks.valid_feed.feed.link)
        self.assertEqual(json_data.get('description'), mocks.valid_feed.feed.description)
        self.assertEqual(json_data.get('xml_link'), self.data.get('url'))
        self.assertEqual(json_data.get('owner'), self.user.pk)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 40)
        item = Item.objects.first()
        self.assertEqual(
            'Qualcomm kondigt eigen smartphone aan met Snapdragon 888 en 6,78"-oledscherm',
            item.title)

    @mock.patch('feeds.utils.parse_feed', return_value=mocks.invalid_feed)
    def test_create_feed_with_invalid_xml(self, feed_mock):
        response = self.client.post(
            '/feeds/',
            data=json.dumps(self.data),
            content_type='application/json'
        )
        json_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(feed_mock.call_count, 1)
        self.assertEqual(Feed.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)
        self.assertEqual('Invalid feed', json_data.get('errors')[0])

    @mock.patch('feeds.utils.parse_feed', return_value=mocks.feed_without_items)
    def test_create_feed_without_items(self, feed_mock):
        response = self.client.post(
            '/feeds/',
            data=json.dumps(self.data),
            content_type='application/json'
        )
        json_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(feed_mock.call_count, 1)
        self.assertEqual(Feed.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)
        self.assertEqual('feed has no items', json_data.get('errors')[0])

    @mock.patch('feeds.utils.parse_feed', return_value=mocks.feed_without_title)
    def test_create_feed_without_title(self, feed_mock):
        response = self.client.post(
            '/feeds/',
            data=json.dumps(self.data),
            content_type='application/json'
        )
        json_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(feed_mock.call_count, 1)
        self.assertEqual(Feed.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)
        self.assertEqual('Invalid feed', json_data.get('errors')[0])

    @mock.patch('feeds.utils.parse_feed', return_value=mocks.item_without_title)
    def test_create_feed_with_items_missing_optional_param(self, feed_mock):
        response = self.client.post(
            '/feeds/',
            data=json.dumps(self.data),
            content_type='application/json'
        )
        json_data = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(feed_mock.call_count, 1)
        self.assertEqual(json_data.get('title'), mocks.valid_feed.feed.title)
        self.assertEqual(json_data.get('link'), mocks.valid_feed.feed.link)
        self.assertEqual(json_data.get('description'), mocks.valid_feed.feed.description)
        self.assertEqual(json_data.get('xml_link'), self.data.get('url'))
        self.assertEqual(json_data.get('owner'), self.user.pk)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 40)
        item = Item.objects.last()
        self.assertIsNone(item.title)

    @mock.patch('feeds.utils.parse_feed', return_value=mocks.item_without_title_and_description)
    def test_create_feed_without_title_and_description(self, feed_mock):
        response = self.client.post(
            '/feeds/',
            data=json.dumps(self.data),
            content_type='application/json'
        )
        json_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(feed_mock.call_count, 1)
        self.assertEqual(Feed.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)
        self.assertEqual('feed has invalid item(s)', json_data.get('errors')[0])

    @mock.patch('feeds.utils.parse_feed', return_value=mocks.valid_feed)
    def test_follow_feed_twice(self, feed_mock):
        FeedFactory(xml_link=self.data['url'], owner=self.user)
        response = self.client.post(
            '/feeds/',
            data=json.dumps(self.data),
            content_type='application/json'
        )
        json_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json_data.get('url'), ['You already following this RSS'])

    @mock.patch('feeds.utils.parse_feed', return_value=mocks.valid_feed)
    def test_follow_feed_followed_by_other_user(self, feed_mock):
        FeedFactory(xml_link=self.data['url'])
        response = self.client.post(
            '/feeds/',
            data=json.dumps(self.data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

    def test_create_feed_with_no_params(self):
        response = self.client.post(
            '/feeds/',
            content_type='application/json'
        )
        json_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json_data.get('url'), ['This field is required.'])

    def test_unfollow_feed(self):
        feed = FeedFactory(owner=self.user)
        ItemFactory.create_batch(5, feed=feed)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 5)
        self.client.delete(
            '/feeds/{}/'.format(feed.pk),
            content_type='application/json'
        )
        self.assertEqual(Feed.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    def test_unfollow_other_user_feed(self):
        feed = FeedFactory()
        response = self.client.delete(
            '/feeds/{}/'.format(feed.pk),
            content_type='application/json'
        )
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(response.status_code, 404)

    def test_list_feeds(self):
        FeedFactory.create_batch(10, owner=self.user)
        response = self.client.get(
            '/feeds/',
            content_type='application/json'
        )
        json_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_data.get("count"), 10)
        self.assertEqual(len(json_data.get("results")), 10)
        for result in json_data.get("results"):
            feed = Feed.objects.get(id=result.get('id'))
            self.assertEqual(result.get('title'), feed.title)
            self.assertEqual(result.get('link'), feed.link)
            self.assertEqual(result.get('description'), feed.description)
            self.assertEqual(result.get('xml_link'), feed.xml_link)
            self.assertEqual(result.get('owner'), self.user.pk)

    def test_list_only_owned_feeds(self):
        FeedFactory.create_batch(10, owner=self.user)
        FeedFactory.create_batch(5)
        response = self.client.get(
            '/feeds/',
            content_type='application/json'
        )
        json_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_data.get("count"), 10)
        for result in json_data.get("results"):
            self.assertEqual(result.get('owner'), self.user.pk)

    @mock.patch('feeds.utils.parse_feed', return_value=mocks.valid_feed)
    def test_successful_force_update(self, feed_mock):
        feed = FeedFactory.create(
            owner=self.user,
            updated=False,
            xml_link=self.data.get('url')
            )
        response = self.client.post(
            '/feeds/{}/force_update/'.format(feed.pk),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(feed_mock.call_count, 1)
        self.assertEqual(json_data.get('title'), mocks.valid_feed.feed.title)
        self.assertEqual(json_data.get('link'), mocks.valid_feed.feed.link)
        self.assertEqual(json_data.get('description'), mocks.valid_feed.feed.description)
        self.assertEqual(json_data.get('xml_link'), self.data.get('url'))
        self.assertEqual(json_data.get('owner'), self.user.pk)
        self.assertTrue(json_data.get('updated'))
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 40)
        feed.refresh_from_db()
        self.assertTrue(feed.updated)

    @mock.patch('feeds.utils.parse_feed', return_value=mocks.invalid_feed)
    def test_unsuccessful_force_update(self, feed_mock):
        feed = FeedFactory.create(
            owner=self.user,
            updated=False,
            xml_link=self.data.get('url')
            )
        response = self.client.post(
            '/feeds/{}/force_update/'.format(feed.pk),
            content_type='application/json'
        )

        json_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual('Invalid feed', json_data.get('errors')[0])
        feed.refresh_from_db()
        self.assertFalse(feed.updated)


class TestItemViewSet(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.feed = FeedFactory(owner=self.user)

    def test_list_items(self):
        ItemFactory.create_batch(4, feed=self.feed)
        response = self.client.get(
            '/items/',
            content_type='application/json'
        )
        json_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_data.get("count"), 4)
        self.assertEqual(len(json_data.get("results")), 4)
        for result in json_data.get("results"):
            item = Item.objects.get(id=result.get('id'))
            self.assertEqual(result.get('title'), item.title)
            self.assertEqual(result.get('link'), item.link)
            self.assertEqual(result.get('read'), item.read)

    def test_list_all_feeds_items(self):
        feed2 = FeedFactory(owner=self.user)
        ItemFactory.create_batch(4, feed=self.feed)
        ItemFactory.create_batch(4, feed=feed2)
        response = self.client.get(
            '/items/',
            content_type='application/json'
        )
        json_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_data.get("count"), 8)
        self.assertEqual(Feed.objects.count(), 2)
        self.assertEqual(Item.objects.count(), 8)

    def test_list_only_owned_feeds_items(self):
        ItemFactory.create_batch(4, feed=self.feed)
        ItemFactory.create_batch(4)
        response = self.client.get(
            '/items/',
            content_type='application/json'
        )
        json_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_data.get("count"), 4)
        self.assertEqual(Item.objects.count(), 8)

        for result in json_data.get("results"):
            item = Item.objects.get(id=result.get('id'))
            self.assertEqual(result.get('feed'), self.feed.id)
            self.assertEqual(item.feed_id, self.feed.id)

    def test_filter_list_items(self):
        ItemFactory.create_batch(4, feed=self.feed, read=True)
        ItemFactory.create_batch(3, feed=self.feed, read=False)
        response = self.client.get(
            '/items/?read=true',
            content_type='application/json'
        )
        json_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_data.get("count"), 4)
        self.assertEqual(len(json_data.get("results")), 4)
        self.assertEqual(Item.objects.count(), 7)
        for result in json_data.get("results"):
            item = Item.objects.get(id=result.get('id'))
            self.assertTrue(item.read)

        response = self.client.get(
            '/items/?read=false',
            content_type='application/json'
        )
        json_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_data.get("count"), 3)
        self.assertEqual(len(json_data.get("results")), 3)
        for result in json_data.get("results"):
            item = Item.objects.get(id=result.get('id'))
            self.assertFalse(item.read)

    def test_list_feed_items(self):
        feed2 = FeedFactory(owner=self.user)
        ItemFactory.create_batch(4, feed=self.feed)
        ItemFactory.create_batch(4, feed=feed2)
        response = self.client.get(
            '/feeds/{}/items/'.format(self.feed.pk),
            content_type='application/json'
        )
        json_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_data.get("count"), 4)
        self.assertEqual(Item.objects.count(), 8)
        for result in json_data.get("results"):
            item = Item.objects.get(id=result.get('id'))
            self.assertEqual(self.feed.pk, item.feed_id)
            self.assertEqual(self.feed.pk, result.get('feed'))

    def test_access_other_user_feed_items(self):
        feed = FeedFactory()
        ItemFactory.create_batch(4, feed=feed)
        response = self.client.get(
            '/feeds/{}/items/'.format(feed.pk),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

    def test_mark_feed_items_read(self):
        items = ItemFactory.create_batch(3, feed=self.feed, read=False)
        response = self.client.post(
            '/feeds/{}/items/read/'.format(self.feed.pk),
            data=json.dumps({"ids": [items[0].id, items[1].id]}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        for item in items:
            item.refresh_from_db()
        self.assertTrue(items[0].read)
        self.assertTrue(items[1].read)
        self.assertFalse(items[2].read)

    def test_mark_items_read(self):
        items = ItemFactory.create_batch(3, feed=self.feed, read=False)
        response = self.client.post(
            '/items/read/',
            data=json.dumps({"ids": [items[0].id, items[1].id]}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        for item in items:
            item.refresh_from_db()
        self.assertTrue(items[0].read)
        self.assertTrue(items[1].read)
        self.assertFalse(items[2].read)

    def test_mark_other_user_item_as_read(self):
        item = ItemFactory.create(read=False)
        response = self.client.post(
            '/items/read/',
            data=json.dumps({"ids": [item.id]}),
            content_type='application/json'
        )
        json_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json_data.get('ids'),
            ['Some ids are invalid or you do not have permission to edit']
        )
        item.refresh_from_db()
        self.assertFalse(item.read)
