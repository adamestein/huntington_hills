from django.conf.urls import url

from .views import (
    AllCurrentNews, AllDataView, EmailNoticeList, MailingAddresses, MainMenuView, NonEmailNoticeList, SignInSheet,
    UpdateBoardMembers, UpdateHomeowners
)


app_name = 'staff'
urlpatterns = [
    url(r'^all_current_news/$', AllCurrentNews.as_view(), name='all_current_news'),
    url(r'^all_data/$', AllDataView.as_view(), name='all_data'),
    url(r'^download/email_notice_list/$', EmailNoticeList.as_view(), name='email_notice_list'),
    url(r'^download/non_email_notice_list/$', NonEmailNoticeList.as_view(), name='non_email_notice_list'),
    url(r'^download/sign_in_sheet/$', SignInSheet.as_view(), name='sign_in_sheet'),
    url(r'^mailing_addresses/$', MailingAddresses.as_view(), name='mailing_addresses'),
    url(r'^main_menu/$', MainMenuView.as_view(), name='main_menu'),
    url(r'^update_board_members/(?P<pk>\d+)$', UpdateBoardMembers.as_view(), name='update_board_members'),
    url(r'^update_homeowners/$', UpdateHomeowners.as_view(), name='update_homeowners')
]
