from django.conf.urls import url

from .views import ResidentListView

app_name = 'resident'
urlpatterns = [
    url(r'^information/$', ResidentListView.as_view(), name='information')
]
