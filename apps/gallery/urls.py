from django.conf.urls import url

from .views import GalleryView, OwnerView, PageView

app_name = 'gallery'
urlpatterns = [
    url(r'^$', GalleryView.as_view(), name='gallery'),
    url(r'^(?P<slug>[\w-]+)/$', OwnerView.as_view(), name='owner'),
    url(r'^(?P<owner_slug>[\w-]+)/page/(?P<page_num>\d+)/$', PageView.as_view(), name='page')
]
