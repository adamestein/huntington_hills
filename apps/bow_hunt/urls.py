from django.conf.urls import url

from .add import AddLogs, FetchLogSheetData
from .daily_log_sheets import FetchLogSheetsByYear, LogSheetView
from .hunters import HunterAnalysis
from .reports.by_hunter import Report as HunterReport

app_name = 'bow_hunt'
urlpatterns = [
    url(r'^analysis/by_hunter/$', HunterAnalysis.as_view(), name='hunter_analysis'),
    url(r'^analysis/by_hunter/report/$', HunterReport.as_view(), name='hunter_report'),
    url(r'^log_sheet/$', LogSheetView.as_view(), name='log_sheet'),
    url(r'^log_sheet/add_logs/$', AddLogs.as_view(), name='add_logs'),
    url(r'^log_sheet/fetch/by_year/locations/$', FetchLogSheetData.as_view(), name='fetch_log_sheet_data'),
    url(r'^log_sheet/fetch/by_year/log_sheets/$', FetchLogSheetsByYear.as_view(), name='fetch_log_sheet_by_year')
]
