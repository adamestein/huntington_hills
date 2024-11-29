from django.conf.urls import url
from django.views.generic import TemplateView


app_name = 'history'
urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='history/history.html'), name='history'),
    url(
        r'^irondequoit_story/$',
        TemplateView.as_view(template_name='history/irondequoit_story.html'),
        name='irondequoit_story'
    ),
url(
        r'^poetry/$',
        TemplateView.as_view(template_name='history/poetry.html'),
        name='poetry'
    ),
    url(
        r'^rochester_ski_club/$',
        TemplateView.as_view(template_name='history/rochester_ski_club.html'),
        name='rochester_ski_club'
    )
]
