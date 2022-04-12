from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.utils.html import escape
from django.views.generic import TemplateView

from .models import LogSheet

from library.views.generic.mixins.ajax import AJAXResponseMixin


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
                if log.incorrect_in_ipd_log:
                    incorrect_log_data = True
                if log.missing_from_ipd_log:
                    missing_log_data = True

                if log.hunter:
                    hunter = {
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
                        'location': log.location.address
                    })
                    prev_location = log.location
                else:
                    # Another hunter at the same location
                    log_data[-1]['hunters'].append(hunter)

            deer_count += log_sheet.deer_taken

            log_sheet_data.append({
                'deer_taken': log_sheet.deer_taken,
                'deer_taken_to_date': deer_count,
                'incorrect_log_data': incorrect_log_data,
                'logs': log_data,
                'missing_log_data': missing_log_data,
                'officer': log_sheet.officer.name,
                'sheet': serializers.serialize('json', [log_sheet])     # serialize() needs an iterable, hence the []
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

        context['years'] = years.keys()

        return context
