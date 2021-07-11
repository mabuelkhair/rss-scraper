import pickle

valid_feed = pickle.load(open("feeds/tests/pickles/valid_feed.pickle", "rb"))
invalid_feed = pickle.load(open("feeds/tests/pickles/invalid_feed.pickle", "rb"))
feed_without_items = pickle.load(open("feeds/tests/pickles/feed_without_items.pickle", "rb"))
feed_without_title = pickle.load(open("feeds/tests/pickles/feed_without_title.pickle", "rb"))
item_without_title_and_description = \
    pickle.load(open("feeds/tests/pickles/item_without_title_and_description.pickle", "rb"))
item_without_title = pickle.load(open("feeds/tests/pickles/item_without_title.pickle", "rb"))
