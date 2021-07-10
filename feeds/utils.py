import feedparser
from time import mktime
from datetime import datetime
from django.utils import timezone

from feeds.models import Item, Feed
from feeds.validators import validate_feed


def parse_feed(feed_url):
    return feedparser.parse(feed_url)


def get_date_object(date):
    return datetime.fromtimestamp(mktime(date), timezone.utc)


def get_feed_data(feed_xml):

    data = {
        "title": feed_xml.feed.get('title'),
        "link": feed_xml.feed.get('link'),
        "description": feed_xml.feed.get('description'),
    }

    if feed_xml.get('modified_parsed'):
        data['modified_at'] = get_date_object(feed_xml.get('modified_parsed'))
    return data


def get_item_data(item):
    data = {
        "title": item.get('title'),
        "link": item.get('link'),
        "description": item.get('description'),
        "guid": item.get('guid'),
    }

    if item.get('published_parsed'):
        data['published_at'] = get_date_object(item.get('published_parsed'))
    return data


def create_items(feed_id, feed_xml):
    items = []
    for item in feed_xml.get('entries'):
        data = get_item_data(item)
        items.append(Item(feed_id=feed_id, **data))
    Item.objects.bulk_create(items)


def update_feed_data(feed, feed_xml):
    feed.updated = True
    data = get_feed_data(feed_xml)
    feed.__dict__.update(data)
    feed.save()


def update_items_data(entries, feed_id):
    for item in entries:
        data = get_item_data(item)
        data['last_updated_at'] = timezone.now()
        Item.objects.update_or_create(guid=data.pop("guid"), feed_id=feed_id, defaults=data)


def feed_has_updates(feed, feed_xml):
    modified_at = get_date_object(feed_xml.get('modified_parsed'))
    if not modified_at:
        return True
    return feed.modified_at != modified_at


def update_feed(feed):
    try:
        feed_xml = parse_feed(feed.xml_link)
        validate_feed(feed_xml)
        if feed_has_updates(feed, feed_xml):
            update_feed_data(feed, feed_xml)
            update_items_data(feed_xml.get('entries'), feed.pk)
        return True
    except Feed.DoesNotExist:
        return False
