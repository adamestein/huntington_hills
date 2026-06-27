from django.urls import re_path

from .views import Archived, ArticleRedirect, ByYear, CurrentArticles

app_name = 'news'
urlpatterns = [
    re_path(r'^archived/$', Archived.as_view(), name='archived'),
    re_path(r'^article/(?P<pk>\d+)$', ArticleRedirect.as_view(), name='article_redirect'),
    re_path(r'^by_year/(?P<year>\d{4})/$', ByYear.as_view(), name='by_year'),
    re_path(r'^by_year/(?P<year>\d{4})/(?P<slug>[\w-]+)$', ByYear.as_view(), name='by_year'),
    re_path(r'^current/$', CurrentArticles.as_view(), name='current_news_articles')
]
