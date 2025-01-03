from django_mailbox.models import Message

from library.views.generic import ProtectedDetailView


class MessageDetailView(ProtectedDetailView):
    model = Message
    template_name = 'mailing_lists/message.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = self.object.get_email_object().get('Date')
        return context
