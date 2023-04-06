from django.urls import path

from authentication import views

urlpatterns = [
    path("signout/", views.signout_view, name="logout"),
    path("signin/", views.signin_view, name="user signin"),
    path("open/", views.last_open_view, name="last open"),
]
