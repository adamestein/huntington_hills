from django.urls import path

from .views import (
    AllCurrentNews, AllDataView, EmailNoticeList, EmailResidentsList, MailingAddresses, MainMenuView,
    NonEmailNoticeList, SignInSheet, UpdateBoardMembers, UpdateHomeowners
)


app_name = 'staff'
urlpatterns = [
    path('all_current_news/', AllCurrentNews.as_view(), name='all_current_news'),
    path('all_data/', AllDataView.as_view(), name='all_data'),
    path('download/email_notice_list/', EmailNoticeList.as_view(), name='email_notice_list'),
    path('download/email_residents_list/', EmailResidentsList.as_view(), name='email_residents_list'),
    path('download/non_email_notice_list/', NonEmailNoticeList.as_view(), name='non_email_notice_list'),
    path('download/sign_in_sheet/', SignInSheet.as_view(), name='sign_in_sheet'),
    path('mailing_addresses/', MailingAddresses.as_view(), name='mailing_addresses'),
    path('main_menu/', MainMenuView.as_view(), name='main_menu'),
    path('update_board_members/<int:pk>', UpdateBoardMembers.as_view(), name='update_board_members'),
    path('update_homeowners/', UpdateHomeowners.as_view(), name='update_homeowners')
]
