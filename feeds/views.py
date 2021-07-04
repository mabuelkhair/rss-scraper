from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from feeds import serializers
from feeds import utils
from feeds import validators
from feeds import models


class FeedViewSet(mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):

    serializer_class = serializers.FeedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.feeds

    def create(self, request, *args, **kwargs):
        create_serializer = serializers.CreateFeedSerializer(
            data=request.data,
            context={'request': request}
            )
        create_serializer.is_valid(raise_exception=True)
        feed = utils.parse_feed(create_serializer.data.get('url'))
        validators.validate_feed(feed)
        data = utils.get_feed_data(feed)
        data['owner'] = request.user.pk
        data['xml_link'] = create_serializer.data.get('url')

        serializer = serializers.FeedSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        utils.create_items(serializer.data.get('id'), feed)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ItemViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):

    serializer_class = serializers.ItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        ids_list = self.request.user.feeds.values_list('pk', flat=True)
        return models.Item.objects.filter(feed_id__in=ids_list)
