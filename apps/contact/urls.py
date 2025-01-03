from django.conf.urls import url
from django.views.generic import TemplateView

from .views import ContactFormView


app_name = 'contact'
urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='contact/contact.html'), name='contact'),
    url(r'^adam/$', ContactFormView.as_view(), {'recipient': 'Adam Stein'}, name='adam'),
    url(r'^board/$', ContactFormView.as_view(), {'recipient': 'Board'}, name='board'),
    url(r'^webmaster/$', ContactFormView.as_view(), {'recipient': 'Webmaster'}, name='webmaster')
]
