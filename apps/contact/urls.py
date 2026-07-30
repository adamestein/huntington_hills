from django.urls import path
from django.views.generic import TemplateView

from .views import ContactFormView


app_name = 'contact'
urlpatterns = [
    path('', TemplateView.as_view(template_name='contact/contact.html'), name='contact'),
    path('adam/', ContactFormView.as_view(), {'recipient': 'Adam Stein'}, name='adam'),
    path('board/', ContactFormView.as_view(), {'recipient': 'Board'}, name='board'),
    path('webmaster/', ContactFormView.as_view(), {'recipient': 'Webmaster'}, name='webmaster')
]
