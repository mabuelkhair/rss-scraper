from rest_framework import generics, mixins
from rest_framework.permissions import IsAuthenticated

from feeds.serializers import FeedSerializer


class FeedAPIView(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  generics.GenericAPIView):

    serializer_class = FeedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.feeds

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
