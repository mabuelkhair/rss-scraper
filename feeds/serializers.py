from rest_framework import serializers

from feeds.models import Feed


class FeedSerializer(serializers.ModelSerializer):

    model = Feed

    class Meta:
        fields = '__all__'
