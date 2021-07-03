from rest_framework.exceptions import ValidationError


def validate_feed(feed):
    if feed.status != 200 or not feed.feed:
        raise ValidationError({"errors": ["Invalid feed"]})
    validate_feed_items(feed)


def validate_feed_items(feed):

    if not feed.get('entries'):
        raise ValidationError({"errors": ["feed has no items"]})

    for item in feed.get('entries'):
        # feed item should has at least title or description
        if not item.get('title') and not item.get('description'):
            raise ValidationError({"errors": ["feed has invalid item(s)"]})
