from rest_framework.exceptions import ValidationError


def validate_feed(feed):
    '''
    Check if parsed feed is valid feed then validate feed items

    Parameters:
        feed (FeedParserDict): FeedParserDict that is generated from parsing the URL.
    '''
    if not feed.get('feed') or feed.get('bozo', 0) == 1:
        raise ValidationError({"errors": ["Invalid feed"]})
    validate_feed_channel(feed.feed)
    validate_feed_items(feed)


def validate_feed_channel(feed):
    '''
    Raise an validation exception if feed is missing any of required param

    Parameters:
        feed (FeedParserDict): FeedParserDict that is generated from parsing the URL.
    '''
    if not feed.get('title') or not feed.get('link') or not feed.get('description'):
        raise ValidationError({"errors": ["Invalid feed"]})


def validate_feed_items(feed):
    '''
    - Validate that feed has items
    - Raise a validation exception if item does neither have title nor description
    - Raise a validation exception if item does not have guid

    Parameters:
        feed (FeedParserDict): FeedParserDict that is generated from parsing the URL.
    '''
    if not feed.get('entries'):
        raise ValidationError({"errors": ["feed has no items"]})

    for item in feed.get('entries'):
        # feed item should has at least title or description
        if not item.get('title') and not item.get('description'):
            raise ValidationError({"errors": ["feed has invalid item(s)"]})

        if not item.get('guid'):
            raise ValidationError({"errors": ["guid is missing in some items"]})
