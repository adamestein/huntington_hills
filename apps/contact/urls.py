from django.urls import re_path
from django.views.generic import TemplateView

from .views import ContactFormView


app_name = 'contact'
urlpatterns = [
    re_path(r'^$', TemplateView.as_view(template_name='contact/contact.html'), name='contact'),
    re_path(r'^adam/$', ContactFormView.as_view(), {'recipient': 'Adam Stein'}, name='adam'),
    re_path(r'^board/$', ContactFormView.as_view(), {'recipient': 'Board'}, name='board'),
    re_path(r'^webmaster/$', ContactFormView.as_view(), {'recipient': 'Webmaster'}, name='webmaster')
]
