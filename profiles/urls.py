from django.urls import path

from profiles import views

urlpatterns = [path("profile/get/", views.get_profile_view, name="get_profile_view")]
