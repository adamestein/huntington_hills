from django.urls import re_path

from library.views.generic import ProtectedTemplateView

from .archives import Archives, ArchiveList
from .by import ByAuthor, ByDate, BySubject, ByThread
from .message import MessageDetailView


app_name = 'mailing_lists'
urlpatterns = [
    re_path(r'^archives/(?P<ml_name_slug>[-\w]+)$', Archives.as_view(), name='archives'),
    re_path(r'^archives/(?P<ml_name_slug>[-\w]+)/byauthor/(?P<archive>[\w ]+)$', ByAuthor.as_view(), name='by_author'),
    re_path(r'^archives/(?P<ml_name_slug>[-\w]+)/bydate/(?P<archive>[\w ]+)$', ByDate.as_view(), name='by_date'),
    re_path(r'^archives/(?P<ml_name_slug>[-\w]+)/bysubject/(?P<archive>[\w ]+)$', BySubject.as_view(), name='by_subject'),
    re_path(r'^archives/(?P<ml_name_slug>[-\w]+)/bythread/(?P<archive>[\w ]+)$', ByThread.as_view(), name='by_thread'),
    re_path(r'^archives/list/$', ArchiveList.as_view(), name='archive_list'),
    re_path(r'^archives/message/(?P<pk>[\d]+)/$', MessageDetailView.as_view(), name='message'),
    re_path(
        r'^lists/$',
        ProtectedTemplateView.as_view(template_name='mailing_lists/lists.html'),
        name='lists'
    ),
]
