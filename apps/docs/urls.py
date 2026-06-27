from django.urls import re_path
from django.views.generic import TemplateView


app_name = 'docs'
urlpatterns = [
    re_path(r'^$', TemplateView.as_view(template_name='docs/docs.html'), name='docs'),
    re_path(
        r'^combined_libraries/$',
        TemplateView.as_view(template_name='docs/Combined_Libraries.html'),
        name='combined_libraries')
]
