from datetime import datetime
import logging

from django.contrib.messages import success
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import ContactForm

logger = logging.getLogger(__name__)

EMAIL_INFORMATION = {
    'Adam Stein': {
        'email': 'adam@csh.rit.edu',
        'subject': 'Adam'
    },
    'Board': {
        'email': 'adam@csh.rit.edu',
        'subject': 'the HH board'
    },
    'Webmaster': {
        'email': 'adam@csh.rit.edu',
        'subject': 'the Webmaster'
    }
}


class ContactFormView(FormView):
    form_class = ContactForm
    success_url = reverse_lazy('contact:contact')
    template_name = 'contact/email_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipient'] = self.kwargs['recipient']

        return context
    def form_valid(self, form):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else self.request.META.get('REMOTE_ADDR')

        message = f'''
Below is the result of your feedback form. It was submitted by
{form.cleaned_data['name']} ({form.cleaned_data['email']}) on {datetime.today().strftime('%A, %B %d, %Y at %H:%M:%S')}
---------------------------------------------------------------------------

name: {form.cleaned_data['name']}

email: {form.cleaned_data['email']}

message: {form.cleaned_data['message']}

---------------------------------------------------------------------------

REMOTE_ADDR: {ip}
HTTP_USER_AGENT: {self.request.META.get('HTTP_USER_AGENT')}
'''

        try:
            send_mail(
                'Huntington Hills Web Email for ' + EMAIL_INFORMATION[self.kwargs['recipient']]['subject'],
                message,
                form.cleaned_data['email'],
                [EMAIL_INFORMATION[self.kwargs['recipient']]['email']]
            )
        except Exception as e:
            logger.error(f'Error sending email from {self.kwargs["recipient"]} form: {e}')

        success(self.request, 'Message sent')
        return super().form_valid(form)