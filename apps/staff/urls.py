from django.urls import re_path

from .views import (
    AllCurrentNews, AllDataView, EmailNoticeList, MailingAddresses, MainMenuView, NonEmailNoticeList, SignInSheet,
    UpdateBoardMembers, UpdateHomeowners
)


app_name = 'staff'
urlpatterns = [
    re_path(r'^all_current_news/$', AllCurrentNews.as_view(), name='all_current_news'),
    re_path(r'^all_data/$', AllDataView.as_view(), name='all_data'),
    re_path(r'^download/email_notice_list/$', EmailNoticeList.as_view(), name='email_notice_list'),
    re_path(r'^download/non_email_notice_list/$', NonEmailNoticeList.as_view(), name='non_email_notice_list'),
    re_path(r'^download/sign_in_sheet/$', SignInSheet.as_view(), name='sign_in_sheet'),
    re_path(r'^mailing_addresses/$', MailingAddresses.as_view(), name='mailing_addresses'),
    re_path(r'^main_menu/$', MainMenuView.as_view(), name='main_menu'),
    re_path(r'^update_board_members/(?P<pk>\d+)$', UpdateBoardMembers.as_view(), name='update_board_members'),
    re_path(r'^update_homeowners/$', UpdateHomeowners.as_view(), name='update_homeowners')
]
