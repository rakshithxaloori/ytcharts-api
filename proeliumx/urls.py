"""proeliumx URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.contrib import admin
from django.urls import path, include


admin_url = "admin"

if os.environ["CI_CD_STAGE"] == "testing" or os.environ["CI_CD_STAGE"] == "production":
    admin_url = os.environ["ADMIN_URL"]


urlpatterns = [
    path("{}/".format(admin_url), admin.site.urls),
    path("authentication/", include("authentication.urls")),
    path("yt/", include("yt.urls")),
]
