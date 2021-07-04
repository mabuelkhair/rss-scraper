from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


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
    title = models.TextField(null=True)
    link = models.URLField(null=True)
    description = models.TextField(null=True)
    published_at = models.DateTimeField(null=True)
    read = models.BooleanField(default=False)
    feed = models.ForeignKey(
        Feed,
        related_name='items',
        on_delete=models.CASCADE
        )

    def clean(self):
        super().clean()
        if self.title is None and self.description is None:
            raise ValidationError('Both title and description can not be None')
