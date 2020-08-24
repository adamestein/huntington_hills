from django.conf.urls import url

from .views import BoardMembersListView, MainMenuView, ResidentListView

app_name = 'resident'
urlpatterns = [
    url(r'^board_members/$', BoardMembersListView.as_view(), name='board'),
    url(r'^information/$', ResidentListView.as_view(), name='information'),
    url(r'^main_menu/$', MainMenuView.as_view(), name='main_menu')
]
