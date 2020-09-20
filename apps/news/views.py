from datetime import date

from django.db.models.functions import Extract
from django.shortcuts import get_object_or_404, reverse
from django.utils.text import slugify
from django.views.generic import RedirectView, TemplateView

from .models import Article


class Archived(TemplateView):
    template_name = 'news/archived.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['years'] = Article.objects.all().dates('posted_on', 'year')\
            .annotate(year=Extract('posted_on', 'year')).values_list('year', flat=True)
        return context


class ArticleRedirect(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        article = get_object_or_404(Article, pk=kwargs['pk'])
        return reverse('news:by_year', args=[article.posted_on.year, slugify(article.title)])


class ByYear(TemplateView):
    template_name = 'news/by_year.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = Article.objects.filter(posted_on__year=kwargs['year'])
        context['slug'] = kwargs.get('slug')    # No slug if showing the entire year
        context['year'] = kwargs['year']
        return context


class CurrentArticles(TemplateView):
    template_name = 'news/current_articles.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = Article.objects.filter(posted_until__gte=date.today())
        return context
