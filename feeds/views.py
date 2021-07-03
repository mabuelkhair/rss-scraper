from types import SimpleNamespace

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from feeds import serializers
from feeds import utils


class FeedViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.FeedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.feeds

    def create(self, request, *args, **kwargs):
        serializer = serializers.CreateFeedSerializer(
            data=request.data,
            context={'request': request}
            )
        serializer.is_valid(raise_exception=True)
        feed = utils.parse_feed(serializer.data.get('url'))
        data = utils.get_feed_data(feed)
        data['owner'] = request.user.pk
        data['xml_link'] = serializer.data.get('url')
        super().create(SimpleNamespace(data=data), *args, **kwargs)
