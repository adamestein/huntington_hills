from django.urls import re_path

from .redirect import redirect


urlpatterns = [
    re_path(r'^redirect/$', redirect, name='redirect')
]
