from django.db import models
from django.conf import settings


class Feed(models.Model):
    title = models.TextField()
    link = models.URLField()
    description = models.TextField()
    xml_link = models.URLField(unique=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='feeds',
        on_delete=models.CASCADE
        )

    class Meta:
        unique_together = ('xml_link', 'owner')


class Item(models.Model):
    title = models.TextField()
    link = models.URLField()
    description = models.TextField()
    published_at = models.DateTimeField()
    read = models.BooleanField(default=False)
    feed = models.ForeignKey(
        Feed,
        related_name='items',
        on_delete=models.CASCADE
        )
