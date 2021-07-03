import feedparser
from time import mktime
from datetime import datetime

from feeds.models import Item


def parse_feed(feed_url):
    return feedparser.parse(feed_url)


def get_feed_data(feed_xml):

    data = {
        "title": feed_xml.feed.get('title'),
        "link": feed_xml.feed.get('link'),
        "description": feed_xml.feed.get('description'),
    }
    return data


def get_item_data(item):
    data = {
        "title": item.get('title'),
        "link": item.get('link'),
        "description": item.get('description'),
        "published_at": datetime.fromtimestamp(mktime(item.get('published_parsed'))),
    }
    return data


def create_items(feed_id, feed_xml):
    items = []
    for item in feed_xml.get('entries'):
        data = get_item_data(item)
        items.append(Item(feed_id=feed_id, **data))
    Item.objects.bulk_create(items)
