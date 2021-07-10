from rest_framework import serializers

from feeds import models


class FeedSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = models.Feed


class CreateFeedSerializer(serializers.Serializer):
    url = serializers.URLField()

    class Meta:
        fields = '__all__'

    def validate_url(self, value):
        user = self.context['request'].user
        if models.Feed.objects.filter(owner=user, xml_link=value).exists():
            raise serializers.ValidationError("You already following this RSS")
        return value


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = models.Item


class ReadItemSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False
        )

    class Meta:
        fields = '__all__'

    def validate_ids(self, value):
        if self.context['items'].filter(id__in=value).count() < len(value):
            raise serializers.ValidationError(
                "Some ids are invalid or you do not have permission to edit"
                )
        return value
