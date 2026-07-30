from django.urls import path

from .redirect import redirect


urlpatterns = [
    path('redirect/', redirect, name='redirect')
]
