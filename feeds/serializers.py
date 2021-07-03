from rest_framework import serializers

from feeds.models import Feed


class FeedSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Feed


class CreateFeedSerializer(serializers.Serializer):
    url = serializers.URLField()

    class Meta:
        fields = '__all__'

    def validate_url(self, value):
        user = self.context['request'].user
        if Feed.objects.filter(owner=user, xml_link=value).exists():
            raise serializers.ValidationError("You already following this RSS")
        return value
