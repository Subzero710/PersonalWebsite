from django.contrib import admin
from django.http import HttpResponse
from django.urls import path

def home(_request):
    return HttpResponse("OK - portfolio up")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home),
]