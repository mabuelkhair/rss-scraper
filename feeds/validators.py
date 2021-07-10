from rest_framework.exceptions import ValidationError


def validate_feed(feed):
    if not feed.feed:
        raise ValidationError({"errors": ["Invalid feed"]})
    validate_feed_channel(feed.feed)
    validate_feed_items(feed)


def validate_feed_channel(feed):
    if not feed.get('title') or not feed.get('link') or not feed.get('description'):
        raise ValidationError({"errors": ["Invalid feed"]})


def validate_feed_items(feed):

    if not feed.get('entries'):
        raise ValidationError({"errors": ["feed has no items"]})

    for item in feed.get('entries'):
        # feed item should has at least title or description
        if not item.get('title') and not item.get('description'):
            raise ValidationError({"errors": ["feed has invalid item(s)"]})

        if not item.get('guid'):
            raise ValidationError({"errors": ["guid is missing in some items"]})
