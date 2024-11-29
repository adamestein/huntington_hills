from django.conf.urls import url
from django.views.generic import TemplateView


app_name = 'docs'
urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='docs/docs.html'), name='docs'),
    url(
        r'^combined_libraries/$',
        TemplateView.as_view(template_name='docs/Combined_Libraries.html'),
        name='combined_libraries')
]
