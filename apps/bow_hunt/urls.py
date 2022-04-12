from django.conf.urls import url

from .views import FetchLogSheetsByYear, LogSheetView

app_name = 'bow_hunt'
urlpatterns = [
    url(r'^log_sheet/$', LogSheetView.as_view(), name='log_sheet'),
    url(r'^log_sheet/fetch/$', FetchLogSheetsByYear.as_view(), name='fetch_log_sheet')
]
