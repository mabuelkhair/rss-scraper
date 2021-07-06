from rest_framework import permissions

from feeds.models import Feed


class IsFeedOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_permission(self, request, view):
        if view.kwargs.get('feed_pk'):
            if not Feed.objects.filter(pk=view.kwargs.get('feed_pk'),
                                       owner_id=request.user.pk).exists():
                return False
        return True
