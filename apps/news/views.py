from django.views.generic import TemplateView


class AllNews(TemplateView):
    template_name = 'news/all_news.html'
