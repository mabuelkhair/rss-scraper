from django.db import models
from django.conf import settings


class Feed(models.Model):
    title = models.TextField()
    link = models.URLField()
    description = models.TextField()
    xml_link = models.URLField(unique=True)
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL)
