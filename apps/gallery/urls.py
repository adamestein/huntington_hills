from django.urls import re_path

from .views import GalleryView, OwnerView, PageView

app_name = 'gallery'
urlpatterns = [
    re_path(r'^$', GalleryView.as_view(), name='gallery'),
    re_path(r'^(?P<slug>[\w-]+)/$', OwnerView.as_view(), name='owner'),
    re_path(r'^(?P<owner_slug>[\w-]+)/page/(?P<page_num>\d+)/$', PageView.as_view(), name='page')
]
