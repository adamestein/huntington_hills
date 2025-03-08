from django.conf.urls import url

from library.views.generic import ProtectedTemplateView

from .archives import Archives, ArchiveList
from .by import ByAuthor, ByDate, BySubject, ByThread
from .message import MessageDetailView


app_name = 'mailing_lists'
urlpatterns = [
    url(r'^archives/(?P<ml_name>[\w ]+)$', Archives.as_view(), name='archives'),
    url(r'^archives/(?P<ml_name>[\w ]+)/byauthor/(?P<archive>[\w ]+)$', ByAuthor.as_view(), name='by_author'),
    url(r'^archives/(?P<ml_name>[\w ]+)/bydate/(?P<archive>[\w ]+)$', ByDate.as_view(), name='by_date'),
    url(r'^archives/(?P<ml_name>[\w ]+)/bysubject/(?P<archive>[\w ]+)$', BySubject.as_view(), name='by_subject'),
    url(r'^archives/(?P<ml_name>[\w ]+)/bythread/(?P<archive>[\w ]+)$', ByThread.as_view(), name='by_thread'),
    url(r'^archives/list/$', ArchiveList.as_view(), name='archive_list'),
    url(r'^archives/message/(?P<pk>[\d]+)/$', MessageDetailView.as_view(), name='message'),
    url(
        r'^lists/$',
        ProtectedTemplateView.as_view(template_name='mailing_lists/lists.html'),
        name='lists'
    ),
]
