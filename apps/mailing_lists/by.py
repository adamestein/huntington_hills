from collections import OrderedDict
from datetime import datetime
from email.utils import parseaddr

from django_mailbox.models import Message

from library.views.generic import ProtectedListView, ProtectedTemplateView

from .models import MailingList, RejectedMessage


class ByAuthor(ProtectedListView):
    template_name = 'mailing_lists/by_author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**self.kwargs)
        context['archive'] = context['archive'].replace('_', ' ')   # Namecheap can't handle spaces in URLs
        return context

    def get_queryset(self):
        month, year = self.kwargs['archive'].split(' ')
        month = datetime.strptime(month, '%B').month

        ml = MailingList.objects.get(name_slug=self.kwargs['ml_name_slug'])
        messages = (
            ml.mailbox.messages
                .exclude(id__in=RejectedMessage.objects.values_list('message_id', flat=True))
                .filter(processed__month=month, processed__year=year)
                .values_list('id', 'subject', 'from_header')
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
        context['archive'] = context['archive'].replace('_', ' ')  # Namecheap can't handle spaces in URLs
        return context

    def get_queryset(self):
        month, year = self.kwargs['archive'].split(' ')
        month = datetime.strptime(month, '%B').month

        ml = MailingList.objects.get(name_slug=self.kwargs['ml_name_slug'])
        messages = (
            ml.mailbox.messages
                .exclude(id__in=RejectedMessage.objects.values_list('message_id', flat=True))
                .filter(processed__month=month, processed__year=year)
                .values_list('id', 'subject', 'from_header')
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
        context['archive'] = context['archive'].replace('_', ' ')  # Namecheap can't handle spaces in URLs
        return context

    def get_queryset(self):
        month, year = self.kwargs['archive'].split(' ')
        month = datetime.strptime(month, '%B').month

        ml = MailingList.objects.get(name_slug=self.kwargs['ml_name_slug'])
        return (
            ml.mailbox.messages
                .exclude(id__in=RejectedMessage.objects.values_list('message_id', flat=True))
                .filter(processed__month=month, processed__year=year)
                .values_list('id', 'subject', 'from_header')
                .order_by('subject')
        )


class ByThread(ProtectedTemplateView):
    template_name = 'mailing_lists/by_thread.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ml = MailingList.objects.get(name_slug=self.kwargs['ml_name_slug'])

        context['archive'] = context['archive'].replace('_', ' ')  # Namecheap can't handle spaces in URLs
        context['threads'] = self._build_thread_hierarchy(context['archive'], ml.mailbox.messages, None)

        return context

    def _build_thread_hierarchy(self, archive, messages, in_reply_to):
        month, year = archive.split(' ')
        month = datetime.strptime(month, '%B').month

        hierarchy = OrderedDict()
        threads = (
            messages
                .exclude(id__in=RejectedMessage.objects.values_list('message_id', flat=True))
                .filter(in_reply_to=in_reply_to, processed__month=month, processed__year=year)
                .values_list('id', 'subject', 'from_header')
                .order_by('id')
        )

        for thread in threads:
            hierarchy[thread] = self._build_thread_hierarchy(archive, messages, thread[0])

        return hierarchy
