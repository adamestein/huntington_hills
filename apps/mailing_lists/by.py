from collections import OrderedDict
from email.utils import parseaddr

from django_mailbox.models import Message

from library.views.generic import ProtectedListView, ProtectedTemplateView

from .models import MailingList, RejectedMessage


class ByAuthor(ProtectedListView):
    template_name = 'mailing_lists/by_author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**self.kwargs)
        return context

    def get_queryset(self):
        ml = MailingList.objects.get(mailbox__name=self.kwargs['ml_name'])
        messages = (
            ml.mailbox.messages
                .exclude(id__in=RejectedMessage.objects.values_list('message_id', flat=True))
                .values_list('id', 'subject', 'from_header')
                .order_by('subject')
        )

        # Sort by full name (if no last name) or last name (if there is one)
        return sorted(messages, key=lambda m: self._format_name(m))

    @staticmethod
    def _format_name(record):
        return parseaddr(record[2])[0].rsplit(' ', maxsplit=1)[-1]


class ByDate(ProtectedListView):
    template_name = 'mailing_lists/by_date.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**self.kwargs)
        return context

    def get_queryset(self):
        ml = MailingList.objects.get(mailbox__name=self.kwargs['ml_name'])
        messages = (
            ml.mailbox.messages
                .exclude(id__in=RejectedMessage.objects.values_list('message_id', flat=True))
                .values_list('id', 'subject', 'from_header')
                .order_by('subject')
        )

        # Sort by full name (if no last name) or last name (if there is one)
        return sorted(messages, key=lambda m: self._get_date(m))

    @staticmethod
    def _get_date(record):
        # Not very efficient to query each message, but not really an issue at the moment as this shouldn't be
        # used much, if at all. If it becomes a problem, we'll fix it.
        return Message.objects.get(id=record[0]).get_email_object().get('Date')


class BySubject(ProtectedListView):
    template_name = 'mailing_lists/by_subject.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**self.kwargs)
        return context

    def get_queryset(self):
        ml = MailingList.objects.get(mailbox__name=self.kwargs['ml_name'])
        return (
            ml.mailbox.messages
                .exclude(id__in=RejectedMessage.objects.values_list('message_id', flat=True))
                .values_list('id', 'subject', 'from_header')
                .order_by('subject')
        )


class ByThread(ProtectedTemplateView):
    template_name = 'mailing_lists/by_thread.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ml = MailingList.objects.get(mailbox__name=self.kwargs['ml_name'])

        context['threads'] = self._build_thread_hierarchy(ml.mailbox.messages, None)

        return context

    def _build_thread_hierarchy(self, messages, in_reply_to):
        hierarchy = OrderedDict()
        threads = (
            messages
                .exclude(id__in=RejectedMessage.objects.values_list('message_id', flat=True))
                .filter(in_reply_to=in_reply_to)
                .values_list('id', 'subject', 'from_header')
                .order_by('id')
        )

        for thread in threads:
            hierarchy[thread] = self._build_thread_hierarchy(messages, thread[0])

        return hierarchy
