import feedparser


def parse_feed(feed_url):
    return feedparser.parse(feed_url)


def get_feed_data(feed_xml):

    data = {
        "title": feed_xml.feed.get('title'),
        "link": feed_xml.feed.get('link'),
        "description": feed_xml.feed.get('description'),
    }
    return data
