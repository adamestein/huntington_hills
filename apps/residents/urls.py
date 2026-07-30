from django.urls import path

from .views import BoardMembersListView, MainMenuView, ResidentListView

app_name = 'resident'
urlpatterns = [
    path('board_members/', BoardMembersListView.as_view(), name='board'),
    path('information/', ResidentListView.as_view(), name='information'),
    path('main_menu/', MainMenuView.as_view(), name='main_menu')
]
