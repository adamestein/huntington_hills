from django.conf.urls import url

from .views import AddLogs, FetchLogSheetsByYear, FetchLogSheetData, LogSheetView

app_name = 'bow_hunt'
urlpatterns = [
    url(r'^log_sheet/$', LogSheetView.as_view(), name='log_sheet'),
    url(r'^log_sheet/add_logs/$', AddLogs.as_view(), name='add_logs'),
    url(r'^log_sheet/fetch/by_year/locations/$', FetchLogSheetData.as_view(), name='fetch_log_sheet_data'),
    url(r'^log_sheet/fetch/by_year/log_sheets/$', FetchLogSheetsByYear.as_view(), name='fetch_log_sheet_by_year')
]
