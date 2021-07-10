from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from feeds import serializers, utils, validators, models
from feeds.permissions import IsFeedOwner


class FeedViewSet(mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):

    serializer_class = serializers.FeedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.feeds.all()

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

    @action(detail=True, methods=['post'])
    def force_update(self, request, pk, *args, **kwargs):
        feed = self.get_object()
        utils.update_feed(feed)
        feed.refresh_from_db()
        return Response(status=status.HTTP_200_OK, data=serializers.FeedSerializer(feed).data)


class ItemViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):

    serializer_class = serializers.ItemSerializer
    permission_classes = [IsAuthenticated, IsFeedOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['read']

    def get_queryset(self):
        if self.kwargs.get('feed_pk'):
            return models.Item.objects.filter(feed_id=self.kwargs.get('feed_pk'))
        ids_list = self.request.user.feeds.values_list('pk', flat=True)
        return models.Item.objects.filter(feed_id__in=ids_list)

    @action(detail=False, methods=['post'])
    def read(self, request, *args, **kwargs):
        serializer = serializers.ReadItemSerializer(
            data=request.data,
            context={'items': self.get_queryset()}
            )
        serializer.is_valid(raise_exception=True)
        models.Item.objects.filter(
            id__in=serializer.validated_data.get('ids')
            ).update(read=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
