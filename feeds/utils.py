from time import mktime
from datetime import datetime
import feedparser
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail

from feeds.models import Item, Feed
from feeds.validators import validate_feed


def parse_feed(feed_url):
    '''
    parse feeds URLs

    Parameters:
        feed_url (URL): Any url parse data from.
    Returns:
        data (FeedParserDict): Feed Parser Object that include data from url.
    '''
    return feedparser.parse(feed_url)


def get_date_object(date):
    '''
    convert struct_time object to date time with utc timezone as
    feedparser normalize any date to utc

    Parameters:
        date (time.struct_time): time structe date.
    Returns:
        date (datetime): datetime object in utc timezone.
    '''
    return datetime.fromtimestamp(mktime(date), timezone.utc)


def get_feed_data(feed_xml):
    '''
    Extract import feed data from feed parsed xml

    Parameters:
        feed_xml (FeedParserDict): All the parsed feed data.
    Returns:
        data (dict): feed important data.
    '''

    data = {
        "title": feed_xml.feed.get('title'),
        "link": feed_xml.feed.get('link'),
        "description": feed_xml.feed.get('description'),
    }

    if feed_xml.get('modified_parsed'):
        data['modified_at'] = get_date_object(feed_xml.get('modified_parsed'))
    return data


def get_item_data(item):
    '''
    Extract import item data from item parsed xml

    Parameters:
        item (FeedParserDict): All the parsed item data.
    Returns:
        data (dict): item important data.
    '''
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
    '''
    Create feed items in database using bulkcreate

    Parameters:
        feed_id (int): the id of the feed that items belong to.
        feed_xml (FeedParserDict): parsed feed data.
    '''
    items = []
    for item in feed_xml.get('entries'):
        data = get_item_data(item)
        items.append(Item(feed_id=feed_id, **data))
    Item.objects.bulk_create(items)


def update_feed_data(feed, feed_xml):
    '''
    Update feed data using data extracted from feed_xml

    Parameters:
        feed (Feed): The feed object to be updated.
        feed_xml (FeedParserDict): parsed feed data.
    '''
    data = get_feed_data(feed_xml)
    feed.__dict__.update(data)
    feed.save()


def update_items_data(entries, feed_id):
    '''
    Update items data if exist or create if item does not exist

    Parameters:
        entries (List): List of items.
        feed_id (int): id of feed that items belongs to.
    '''
    for item in entries:
        data = get_item_data(item)
        data['last_updated_at'] = timezone.now()
        Item.objects.update_or_create(guid=data.pop("guid"), feed_id=feed_id, defaults=data)


def feed_has_updates(feed, feed_xml):
    '''
    check if feed has update by comparing last modification dates

    Parameters:
        feed (Feed): Feed object that we already have.
        feed_xml (FeedParserDict): New parsed data.
    Returns:
        updated (boolean): True if there is difference between database and parsed data, false otherwise.
    '''
    modified_at = get_date_object(feed_xml.get('modified_parsed'))
    if not modified_at:
        return True
    return feed.modified_at != modified_at


def update_feed(feed):
    '''
    check if feed is valid and has update then update feed and its items

    Parameters:
        feed (Feed): Feed object to be updated.
    Returns:
        updated (boolean): False if update failed and True otherwise.
    '''
    try:
        feed_xml = parse_feed(feed.xml_link)
        validate_feed(feed_xml)
        if feed_has_updates(feed, feed_xml):
            update_feed_data(feed, feed_xml)
            update_items_data(feed_xml.get('entries'), feed.pk)
        feed.updated = True
        feed.save()
        return True
    except Feed.DoesNotExist:
        return False


def send_failure_notification(feed):
    '''
    send notification email to the user who owns the feed that failed to be updated

    Parameters:
        feed (Feed): Feed object that failed to be updated.
    '''

    subject = 'Failed to update feed'
    message = \
        'Hi {}, System faild to update this feed ({}) and auto updating is disabled for this feed.'.format(
            feed.owner.username,
            feed.xml_link
        )
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [feed.owner.email, ]
    send_mail(subject, message, email_from, recipient_list)
