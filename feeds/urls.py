from django.urls import path

from feeds import views

urlpatterns = [
    path('', views.FeedAPIView.as_view())
]
