import json
from unittest import mock

from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .factories import UserFactory, FeedFactory
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
