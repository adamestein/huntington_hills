import json
import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import success
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import FormView, TemplateView

from .forms import (
    DEER_PREFIX, HUNTER_PREFIX, DeerForm, DeerFormSet, HunterForm, HunterFormSet, LocationForm, LogSheetForm
)
from .models import Location, Log, LogSheet

from library.contrib.auth.mixins import IsBowHuntMixin
from library.views.generic.mixins.ajax import AJAXResponseMixin


class AddLogs(LoginRequiredMixin, IsBowHuntMixin, FormView):
    form_class = LogSheetForm
    template_name = 'bow_hunt/add_logs.html'
    success_url = reverse_lazy('bow_hunt:add_logs')

    def form_valid(self, *args):
        form, hunter_formset = args
        log_sheet = form.cleaned_data['log_sheet']
        log_ids = {}

        # Save all the locations that had hunters
        for hunter_form in hunter_formset.forms:
            if hunter_form.cleaned_data['pk']:
                hunter_form.instance = Log.objects.get(pk=hunter_form.cleaned_data['pk'])
            log = hunter_form.save(commit=False)
            if hunter_form.cleaned_data['pk'] is None:
                log.location = Location.objects.get(id=hunter_form.cleaned_data['location_id'])
                log.log_sheet = log_sheet
            log.save()
            log_ids[hunter_form.cleaned_data['hunter_formset_number']] = log.id
            hunter_form.save_m2m()

        # We'll update the POST data to contain the correct 'log' ID for the deer forms so that they can be
        # validated and saved properly
        post_data = self.request.POST.copy()

        for key in post_data:
            matches = re.match(r'deer-([0-9]+)-log', key)
            if matches:
                post_data[matches.string] = log_ids[int(post_data[f'deer-{matches.group(1)}-hunter_formset_number'])]

        deer_formset = DeerFormSet(post_data, form_kwargs={'log_required': True}, prefix=DEER_PREFIX)
        if deer_formset.is_valid():
            for deer_form in deer_formset.forms:
                if deer_form.cleaned_data['count']:
                    # Only need to save when there is a count, otherwise, why bother? No DB entry = no deer shot
                    deer_form.save()
        else:
            return self.form_invalid(form, hunter_formset, self.request.POST['log_sheet'], deer_formset)

        num_logs = len(hunter_formset.forms)
        success(
            self.request,
            f'Successfully added/updated {num_logs} log{"s"[:num_logs ^ 1]} to the {form.cleaned_data["log_sheet"]}'
        )

        return super().form_valid(form)

    def form_invalid(self, *args):
        form, hunter_formset, log_sheet_id, deer_formset = args

        return self.render_to_response(
            self.get_context_data(
                deer_formset=deer_formset, form=form, hunter_formset=hunter_formset, log_sheet_id=log_sheet_id
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'deer_formset' not in context:
            context['deer_formset'] = DeerFormSet(prefix=DEER_PREFIX)
            deer_forms = None
        else:
            deer_forms = {}
            for form in context['deer_formset'].forms:
                data = str(form)
                pk = form.cleaned_data['log'].pk
                if pk in deer_forms:
                    deer_forms[pk].append(data)
                else:
                    deer_forms[pk] = [data]

        if 'hunter_formset' not in context:
            context['hunter_formset'] = HunterFormSet(prefix=HUNTER_PREFIX)
        else:
            # We'll put the hunter formset forms into a format that will be easier to load on the page
            data = []
            for form in context['hunter_formset'].forms:
                data.append({
                    'deer': deer_forms[form.instance.pk],
                    'form': str(form),
                    'location_id': form.cleaned_data['location_id'],
                    'no_hunter': form.cleaned_data['hunter'] is None,
                    'prefix': form.prefix
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

        hunter_formset = HunterFormSet(self.request.POST, prefix=HUNTER_PREFIX)

        if hunter_formset.is_valid():
            return self.form_valid(form, hunter_formset)
        else:
            return self.form_invalid(form, hunter_formset, self.request.POST['log_sheet'], None)


class FetchLogSheetData(LoginRequiredMixin, IsBowHuntMixin, AJAXResponseMixin, TemplateView):
    content_type = 'application/json'

    def get_context_data(self, **kwargs):
        log_sheet = LogSheet.objects.get(id=self.request.GET['sheet_id'])
        query = Log.objects.filter(log_sheet=log_sheet).values_list('location', flat=True)

        deer_index = 0
        log_forms = []

        for index, log in enumerate(Log.objects.filter(log_sheet=log_sheet)):
            deer_info = []
            for deer in log.deer_set.all():
                deer_info.append(str(DeerForm(instance=deer, prefix=f'{DEER_PREFIX}-{deer_index}')))
                deer_index += 1

            # JavaScript/jQuery needs easy access to a few items, so we'll add an easy-to-get-to copy.
            log_forms.append(
                {
                    'deer': deer_info,
                    'form': str(
                        HunterForm(
                            initial={
                                'location_id': log.location_id,
                                'log_sheet_id': log.log_sheet_id,
                                'pk': log.pk
                            },
                            instance=log,
                            prefix=f'{HUNTER_PREFIX}-{index}'
                        )
                    ),
                    'location_id': log.location_id,
                    'log_id': log.id,
                    'no_hunter': log.hunter is None,
                    'prefix': f'{HUNTER_PREFIX}-{index}'
                }
            )

        context = {
            'log_forms': log_forms,
            'locations': str(LocationForm(initial={'location': query}, year=log_sheet.date.year).as_p())
        }

        return context