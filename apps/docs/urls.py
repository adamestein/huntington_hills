from django.urls import path
from django.views.generic import TemplateView


app_name = 'docs'
urlpatterns = [
    path('', TemplateView.as_view(template_name='docs/docs.html'), name='docs'),
    path(
        'combined_libraries/',
        TemplateView.as_view(template_name='docs/Combined_Libraries.html'),
        name='combined_libraries')
]
