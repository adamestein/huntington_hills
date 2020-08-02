from django.conf.urls import url

from .redirect import redirect


urlpatterns = [
    url(r'^redirect/$', redirect, name='redirect')
]
