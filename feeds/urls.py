from rest_framework.routers import DefaultRouter

from feeds import views

router = DefaultRouter()
router.register('', views.FeedViewSet, basename='feeds')
urlpatterns = router.urls
