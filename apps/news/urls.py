from django.conf.urls import url

from .views import Archived, ArticleRedirect, ByYear, CurrentArticles

app_name = 'news'
urlpatterns = [
    url(r'^archived/$', Archived.as_view(), name='archived'),
    url(r'^article/(?P<pk>\d+)$', ArticleRedirect.as_view(), name='article_redirect'),
    url(r'^by_year/(?P<year>\d{4})/$', ByYear.as_view(), name='by_year'),
    url(r'^by_year/(?P<year>\d{4})/(?P<slug>[\w-]+)$', ByYear.as_view(), name='by_year'),
    url(r'^current/$', CurrentArticles.as_view(), name='current_news_articles')
]
