from django.http import JsonResponse
from django.urls import path

from core.views import home


def health(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("", home),
    path("health", health),
]
