from django.urls import re_path
from django.views.generic import TemplateView


app_name = 'history'
urlpatterns = [
    re_path(r'^$', TemplateView.as_view(template_name='history/history.html'), name='history'),
    re_path(
        r'^irondequoit_story/$',
        TemplateView.as_view(template_name='history/irondequoit_story.html'),
        name='irondequoit_story'
    ),
    re_path(
        r'^poetry/$',
        TemplateView.as_view(template_name='history/poetry.html'),
        name='poetry'
    ),
    re_path(
        r'^rochester_ski_club/$',
        TemplateView.as_view(template_name='history/rochester_ski_club.html'),
        name='rochester_ski_club'
    )
]
