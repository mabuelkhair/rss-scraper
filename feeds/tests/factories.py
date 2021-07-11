from django.contrib.auth import get_user_model
from django.utils.timezone import now
import factory

from feeds.models import Feed, Item


class UserFactory(factory.Factory):
    username = factory.Sequence(lambda n: 'user%d' % n)
    password = factory.Faker('password')

    @factory.lazy_attribute
    def email(self):
        return '%s@example.com' % self.username

    class Meta:
        model = get_user_model()


class FeedFactory(factory.Factory):
    title = factory.Faker("sentence", nb_words=3)
    link = factory.Faker("url")
    description = factory.Faker("sentence", nb_words=7)
    xml_link = factory.Faker('url')
    owner = factory.SubFactory(UserFactory)
    modified_at = factory.LazyFunction(now)
    updated = factory.Faker('pybool')

    class Meta:
        model = Feed


class ItemFactory(factory.Factory):
    title = factory.Faker("sentence", nb_words=3)
    link = factory.Faker("url")
    description = factory.Faker("sentence", nb_words=7)
    published_at = factory.LazyFunction(now)
    read = factory.Faker('pybool')
    feed = factory.SubFactory(FeedFactory)
    last_updated_at = factory.LazyFunction(now)
    guid = factory.Faker("sentence", nb_words=1)

    class Meta:
        model = Item
