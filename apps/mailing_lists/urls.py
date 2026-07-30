from django.urls import path

from library.views.generic import ProtectedTemplateView

from .archives import Archives, ArchiveList
from .by import ByAuthor, ByDate, BySubject, ByThread
from .message import MessageDetailView


app_name = 'mailing_lists'
urlpatterns = [
    path('archives/<slug:ml_name_slug>', Archives.as_view(), name='archives'),
    path('archives/<slug:ml_name_slug>/byauthor/<str:archive>', ByAuthor.as_view(), name='by_author'),
    path('archives/<slug:ml_name_slug>/bydate/<str:archive>', ByDate.as_view(), name='by_date'),
    path('archives/<slug:ml_name_slug>/bysubject/<str:archive>', BySubject.as_view(), name='by_subject'),
    path('archives/<slug:ml_name_slug>/bythread/<str:archive>', ByThread.as_view(), name='by_thread'),
    path('archives/list/', ArchiveList.as_view(), name='archive_list'),
    path('archives/message/<int:pk>/', MessageDetailView.as_view(), name='message'),
    path(
        'lists/',
        ProtectedTemplateView.as_view(template_name='mailing_lists/lists.html'),
        name='lists'
    ),
]
