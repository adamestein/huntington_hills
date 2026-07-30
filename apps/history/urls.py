from django.urls import path
from django.views.generic import TemplateView


app_name = 'history'
urlpatterns = [
    path('', TemplateView.as_view(template_name='history/history.html'), name='history'),
    path(
        'irondequoit_story/',
        TemplateView.as_view(template_name='history/irondequoit_story.html'),
        name='irondequoit_story'
    ),
    path(
        'poetry/',
        TemplateView.as_view(template_name='history/poetry.html'),
        name='poetry'
    ),
    path(
        'rochester_ski_club/',
        TemplateView.as_view(template_name='history/rochester_ski_club.html'),
        name='rochester_ski_club'
    )
]
