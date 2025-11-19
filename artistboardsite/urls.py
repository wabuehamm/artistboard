"""
URL configuration for artistboardsite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import include, path
from django.views.generic import RedirectView


def media(request, file_path=None):
    from django.conf import settings as cfg

    media_root = getattr(cfg, "MEDIA_ROOT", None)

    if not media_root:
        return HttpResponseBadRequest("Invalid Media Root Configuration")
    if not file_path:
        return HttpResponseBadRequest("Invalid File Path")

    with open(os.path.join(media_root, file_path), "rb") as doc:
        response = HttpResponse(doc.read(), content_type="application/doc")
        response["Content-Disposition"] = "filename=%s" % (file_path.split("/")[-1])
        return response


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("artistboard.urls")),
    path("", RedirectView.as_view(url="/home")),
    path("api/", include("artistboard.api")),
    path("media/<str:file_path>", media, name="media"),
]
