from django.urls import re_path

from .add import AddIPDFinalReport, AddLogs, AddNonIPDLogs, FetchLogSheetData
from .commons import CommonsHunting
from .daily_log_sheets import FetchLogSheetsByYear, LogSheetView
from .analysis import HunterAnalysis, LocationAnalysis, SiteAnalysis

app_name = 'bow_hunt'
urlpatterns = [
    re_path(r'^analysis/by_hunter/$', HunterAnalysis.as_view(), name='hunter_analysis'),
    re_path(r'^analysis/by_location/$', LocationAnalysis.as_view(), name='location_analysis'),
    re_path(r'^analysis/by_site/$', SiteAnalysis.as_view(), name='site_analysis'),
    re_path(r'^commons/$', CommonsHunting.as_view(), name='commons_hunting'),
    re_path(r'^log_sheet/$', LogSheetView.as_view(), name='log_sheet'),
    re_path(r'^log_sheet/add/ipd_final_report/$', AddIPDFinalReport.as_view(), name='add_ipd_final_report'),
    re_path(r'^log_sheet/add/logs/$', AddLogs.as_view(), name='add_logs'),
    re_path(r'^log_sheet/add/non_ipd_logs/$', AddNonIPDLogs.as_view(), name='add_non_ipd_logs'),
    re_path(r'^log_sheet/fetch/by_year/locations/$', FetchLogSheetData.as_view(), name='fetch_log_sheet_data'),
    re_path(r'^log_sheet/fetch/by_year/log_sheets/$', FetchLogSheetsByYear.as_view(), name='fetch_log_sheet_by_year')
]
