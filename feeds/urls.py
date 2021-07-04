from django.urls import path, include
from rest_framework_nested import routers

from feeds import views

router = routers.SimpleRouter()
router.register('feeds', views.FeedViewSet, basename='feeds')
feed_router = routers.NestedSimpleRouter(router, 'feeds', lookup='feed')
feed_router.register('items', views.ItemViewSet, basename='feed-items')
urlpatterns = [
    path('', include(router.urls)),
    path('', include(feed_router.urls)),
]
