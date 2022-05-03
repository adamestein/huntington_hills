import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import success
from django.core import serializers
from django.utils.html import escape
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import FormView, TemplateView

from .forms import HunterForm, HunterFormSet, LocationForm, LogSheetForm
from .models import Location, Log, LogSheet

from library.views.generic.mixins.ajax import AJAXResponseMixin


class AddLogs(LoginRequiredMixin, FormView):
    form_class = LogSheetForm
    template_name = 'bow_hunt/add_logs.html'
    success_url = reverse_lazy('bow_hunt:add_logs')

    def form_valid(self, *args):
        form, hunter_formset = args
        log_sheet = form.cleaned_data['log_sheet']

        # Save all the locations that had hunters
        for hunter_form in hunter_formset.forms:
            log = hunter_form.save(commit=False)
            if hunter_form.cleaned_data['pk'] is None:
                log.location = Location.objects.get(id=hunter_form.cleaned_data['location_id'])
                log.log_sheet = log_sheet
            log.save()
            hunter_form.save_m2m()

        num_logs = len(hunter_formset.forms)
        success(
            self.request,
            f'Successfully added/updated {num_logs} log{"s"[:num_logs ^ 1]} to the {form.cleaned_data["log_sheet"]}'
        )

        return super().form_valid(form)

    def form_invalid(self, *args):
        form, hunter_formset, log_sheet_id = args

        return self.render_to_response(
            self.get_context_data(form=form, hunter_formset=hunter_formset, log_sheet_id=log_sheet_id)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'hunter_formset' not in context:
            context['hunter_formset'] = HunterFormSet()
        else:
            # We'll put the hunter formset forms into a format that will be easier to load on the page
            data = []
            for form in context['hunter_formset'].forms:
                data.append({
                    'form': str(form),
                    'location_id': form.cleaned_data['location_id'],
                    'no_hunter': form.cleaned_data['hunter'] is None
                })
            context['hunter_forms'] = json.dumps(data)

        if 'log_sheet_id' in context:
            location_ids = [self.request.POST[key] for key in self.request.POST if 'location_id' in key]
            year = LogSheet.objects.get(id=context['log_sheet_id']).date.year

            context['locations'] = mark_safe(str(LocationForm(initial={'location': location_ids}, year=year).as_p()))
            initial = {'log_sheet': context['log_sheet_id']}
        else:
            initial = {}

        context['log_sheet_form'] = LogSheetForm(initial=initial)

        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        form.is_valid()     # The form for this view is always valid

        hunter_formset = HunterFormSet(self.request.POST)

        if hunter_formset.is_valid():
            return self.form_valid(form, hunter_formset)
        else:
            return self.form_invalid(form, hunter_formset, self.request.POST['log_sheet'])


class FetchLogSheetData(LoginRequiredMixin, AJAXResponseMixin, TemplateView):
    content_type = 'application/json'

    def get_context_data(self, **kwargs):
        log_sheet = LogSheet.objects.get(id=self.request.GET['sheet_id'])
        query = Log.objects.filter(log_sheet=log_sheet).values_list('location', flat=True)

        log_forms = []
        for index, log in enumerate(Log.objects.filter(log_sheet=log_sheet)):
            # JavaScript/jQuery needs easy access to a few items, so we'll add an easy-to-get-to copy.
            log_forms.append(
                {
                    'form': str(
                        HunterForm(
                            initial={
                                'location_id': log.location_id,
                                'log_sheet_id': log.log_sheet_id,
                                'pk': log.pk
                            },
                            instance=log,
                            prefix=f'form-{index}'
                        )
                    ),
                    'location_id': log.location_id,
                    'log_id': log.id,
                    'no_hunter': log.hunter is None
                }
            )

        context = {
            'log_forms': log_forms,
            'locations': str(LocationForm(initial={'location': query}, year=log_sheet.date.year).as_p())
        }

        return context


class FetchLogSheetsByYear(LoginRequiredMixin, AJAXResponseMixin, TemplateView):
    content_type = 'application/json'

    def get_context_data(self, **kwargs):
        deer_count = 0
        incorrect_log_data = False
        log_sheet_data = []
        missing_log_data = False

        for log_sheet in LogSheet.objects.filter(date__year=self.request.GET['year']):
            log_data = []
            prev_location = None

            for log in log_sheet.log_set.all().order_by('location', 'hunter__last_name', 'hunter__first_name'):
                if log.incorrect_warnings.all().exists():
                    incorrect_log_data = True
                if log.missing_warnings.all().exists():
                    missing_log_data = True

                if log.hunter:
                    hunter = {
                        'comment': escape(log.comment),
                        'deer': log.deer_as_str,
                        'name': escape(log.hunter.name),
                        'track': log.deer_tracking
                    }
                else:
                    hunter = None

                if log.location != prev_location:
                    # First time for this location
                    log_data.append({
                        'hunters': None if hunter is None else [hunter],
                        'incorrect_warnings': serializers.serialize('json', log.incorrect_warnings.all()),
                        'loc_index': log.location.line_number,
                        'location': log.location.address,
                        'missing_warnings': serializers.serialize('json', log.missing_warnings.all())
                    })
                    prev_location = log.location
                else:
                    # Another hunter at the same location
                    try:
                        log_data[-1]['hunters'].append(hunter)
                    except AttributeError as e:
                        if log_data[-1]['hunters'] is None:
                            e.args = (
                                f'Data error: location "{log.location}" has multiple entries for {log_sheet.date} '
                                'that shouldn\'t exist',
                            )
                        raise

            deer_count += log_sheet.deer_taken

            log_sheet_data.append({
                'deer_taken': log_sheet.deer_taken,
                'deer_taken_to_date': deer_count,
                'incorrect_log_data': incorrect_log_data,
                'logs': log_data,
                'missing_log_data': missing_log_data,
                'officer': log_sheet.officer.name,
                'sheet': serializers.serialize('json', [log_sheet]),    # serialize() needs an iterable, hence the []
                'total_archers': log_sheet.total_archers
            })

        return log_sheet_data


class LogSheetView(LoginRequiredMixin, TemplateView):
    template_name = 'bow_hunt/log_sheet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Can't get distinct() to work with MySQL, so we'll do it by hand to get a distinct list of years
        years = {}
        for log_sheet in LogSheet.objects.all():
            years[log_sheet.date.year] = True

        # If there is any info on 2017 hunting, can remove the addition (IPD did not keep log in 2017)
        context['years'] = ['2017'] + list(years.keys())

        return context
