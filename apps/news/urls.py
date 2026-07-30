from django.urls import path

from .views import Archived, ArticleRedirect, ByYear, CurrentArticles

app_name = 'news'
urlpatterns = [
    path('archived/', Archived.as_view(), name='archived'),
    path('article/<int:pk>', ArticleRedirect.as_view(), name='article_redirect'),
    path('by_year/<int:year>/', ByYear.as_view(), name='by_year'),
    path('by_year/<int:year>/<slug:slug>', ByYear.as_view(), name='by_year'),
    path('current/', CurrentArticles.as_view(), name='current_news_articles')
]
