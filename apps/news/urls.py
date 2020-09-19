from django.conf.urls import url

from .views import AllNews

app_name = 'news'
urlpatterns = [
    url(r'^all/$', AllNews.as_view(), name='all_news')
]
