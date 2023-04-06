from django.urls import path

from yt import views

urlpatterns = [
    path("connect/check/", views.check_connected_view, name="check if yt connected"),
    path("connect/", views.connect_yt_view, name="create channels and keys"),
]
