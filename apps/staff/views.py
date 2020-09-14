from easy_pdf.views import PDFTemplateView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import success
from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy

from .forms import UpdateHomeownersFormSet

from library.contrib.auth.mixins import IsStaffMixin
from library.views.generic.csv import CSVFileView

from residents.models import Email, EmailType, Person, Property, Street


class AllDataView(LoginRequiredMixin, IsStaffMixin, TemplateView):
    template_name = 'staff/all_data.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['properties'] = Property.objects.all()
        context['emails'] = {}
        context['email_types'] = EmailType.objects.all().values_list('email_type', flat=True)

        for residential_property in context['properties']:
            context['emails'][residential_property.id] = {}
            for email_type in EmailType.objects.all():
                context['emails'][residential_property.id][email_type.email_type] = Email.objects.filter(
                    email_type=email_type, person__active=True, person__residential_property=residential_property
                ).order_by('email')

        return context


class EmailNoticeList(LoginRequiredMixin, IsStaffMixin, CSVFileView):
    csv_filename = 'email_notice_list.csv'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['data'] = [['', 'Names', 'Address', 'Emails'], []]

        for street in Street.objects.all():
            context['data'].append([street.street])

            for residential_property in Property.objects.filter(street=street):
                emails = []
                people = []

                for person in residential_property.get_all_active_people():
                    if person.has_notice_email:
                        emails.append(person.email_set.get(email_type__email_type=EmailType.NOTIFICATION).email)
                        people.append(person.full_name)

                if people:
                    context['data'].append(
                        ['', '\n'.join(people), residential_property.street_address(), '\n'.join(emails)]
                    )

            context['data'].append([])

        return context


class MailingAddresses(LoginRequiredMixin, IsStaffMixin, TemplateView):
    template_name = 'staff/mailing_addresses.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['properties'] = Property.objects.all()
        return context


class MainMenuView(LoginRequiredMixin, IsStaffMixin, TemplateView):
    template_name = 'staff/main_menu.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_main_menu'] = True
        return context


class NonEmailNoticeList(LoginRequiredMixin, IsStaffMixin, CSVFileView):
    csv_filename = 'non_email_notice_list.csv'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['data'] = []

        for street in Street.objects.all():
            context['data'].append([street.street])

            for residential_property in Property.objects.filter(street=street):
                if not residential_property.receives_email_notices:
                    context['data'].append(['', residential_property.mailing_address(include_names=True)])

            context['data'].append([])

        return context


class SignInSheet(LoginRequiredMixin, IsStaffMixin, PDFTemplateView):
    pdf_filename = 'sign_in_sheet.pdf'
    template_name = 'staff/annual_meeting_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            pagesize='letter',
            title='Attendees Sign In Sheet',
            **kwargs
        )
        context['properties'] = Property.objects.all()

        return context


class UpdateHomeowners(LoginRequiredMixin, IsStaffMixin, FormView):
    form_class = UpdateHomeownersFormSet
    success_url = reverse_lazy('staff:update_homeowners')
    template_name = 'staff/update_homeowners.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['properties_by_street'] = {}

        for street in Street.objects.all():
            context['properties_by_street'][street.street] = Property.objects.filter(street=street)

        return context

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
            'queryset': Person.objects.none(),
            'unrequired': [1]
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def form_valid(self, form):
        residential_property = Property.objects.get(id=self.request.POST['property'])

        # Deactivate the old property owners
        Person.objects.filter(residential_property=residential_property).update(active=False)

        for person_form in form.forms:
            if person_form.cleaned_data:
                # Add the new property owners
                person = person_form.save(commit=False)
                person.residential_property = residential_property
                person.save()

        success(self.request, 'Updated Homeowners')

        return super().form_valid(form)
