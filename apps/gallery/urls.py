from django.urls import path

from .views import GalleryView, OwnerView, PageView

app_name = 'gallery'
urlpatterns = [
    path('', GalleryView.as_view(), name='gallery'),
    path('<slug:slug>/', OwnerView.as_view(), name='owner'),
    path('<slug:owner_slug>/page/<int:page_num>/', PageView.as_view(), name='page')
]
