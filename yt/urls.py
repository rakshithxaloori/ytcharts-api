from django.urls import path

from yt import views

urlpatterns = [
    path("connect/post/", views.connect_yt_view, name="create channels and keys"),
    path("get/views/", views.get_views_view, name="get views"),
]
