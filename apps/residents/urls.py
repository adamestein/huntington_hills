from django.urls import re_path

from .views import BoardMembersListView, MainMenuView, ResidentListView

app_name = 'resident'
urlpatterns = [
    re_path(r'^board_members/$', BoardMembersListView.as_view(), name='board'),
    re_path(r'^information/$', ResidentListView.as_view(), name='information'),
    re_path(r'^main_menu/$', MainMenuView.as_view(), name='main_menu')
]
