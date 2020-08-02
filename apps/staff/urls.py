from django.conf.urls import url

from .views import AllDataView, EmailNoticeList, MailingAddresses, MainMenuView, NonEmailNoticeList, SignInSheet


app_name = 'staff'
urlpatterns = [
    url(r'^all_data/$', AllDataView.as_view(), name='all_data'),
    url(r'^download/email_notice_list/$', EmailNoticeList.as_view(), name='email_notice_list'),
    url(r'^download/non_email_notice_list/$', NonEmailNoticeList.as_view(), name='non_email_notice_list'),
    url(r'^download/sign_in_sheet/$', SignInSheet.as_view(), name='sign_in_sheet'),
    url(r'^mailing_addresses/$', MailingAddresses.as_view(), name='mailing_addresses'),
    url(r'^main_menu/$', MainMenuView.as_view(), name='main_menu')
]
