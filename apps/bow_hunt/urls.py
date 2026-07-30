from django.urls import path

from .add import AddIPDFinalReport, AddLogs, AddNonIPDLogs, FetchLogSheetData
from .commons import CommonsHunting
from .daily_log_sheets import FetchLogSheetsByYear, LogSheetView
from .analysis import HunterAnalysis, LocationAnalysis, SiteAnalysis

app_name = 'bow_hunt'
urlpatterns = [
    path('analysis/by_hunter/', HunterAnalysis.as_view(), name='hunter_analysis'),
    path('analysis/by_location/', LocationAnalysis.as_view(), name='location_analysis'),
    path('analysis/by_site/', SiteAnalysis.as_view(), name='site_analysis'),
    path('commons/', CommonsHunting.as_view(), name='commons_hunting'),
    path('log_sheet/', LogSheetView.as_view(), name='log_sheet'),
    path('log_sheet/add/ipd_final_report/', AddIPDFinalReport.as_view(), name='add_ipd_final_report'),
    path('log_sheet/add/logs/', AddLogs.as_view(), name='add_logs'),
    path('log_sheet/add/non_ipd_logs/', AddNonIPDLogs.as_view(), name='add_non_ipd_logs'),
    path('log_sheet/fetch/by_year/locations/', FetchLogSheetData.as_view(), name='fetch_log_sheet_data'),
    path('log_sheet/fetch/by_year/log_sheets/', FetchLogSheetsByYear.as_view(), name='fetch_log_sheet_by_year')
]
