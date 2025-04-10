from django.db.models.functions import TruncMonth

from library.views.generic import ProtectedListView, ProtectedTemplateView

from .models import MailingList


class ArchiveList(ProtectedListView):
    model = MailingList
    template_name = 'mailing_lists/archive_list.html'


class Archives(ProtectedTemplateView):
    template_name = 'mailing_lists/archives.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['archives'] = []

        ml = MailingList.objects.get(name_slug=self.kwargs['ml_name_slug'])
        msg_groups = (
            ml.mailbox.messages
                .values('processed')
                .annotate(month=TruncMonth('processed'))
                .values('month')
                .distinct()
                .order_by('month')
        )

        context['ml_name'] = ml.mailbox.name
        context['ml_name_slug'] = ml.name_slug

        for msg_group in msg_groups:
            context['archives'].append(msg_group['month'].strftime('%B %Y'))

        return context
