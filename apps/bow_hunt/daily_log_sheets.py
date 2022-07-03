import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.utils.html import escape
from django.views.generic import TemplateView

from .models import LogSheet

from library.contrib.auth.mixins import IsBowHuntMixin
from library.views.generic.mixins.ajax import AJAXResponseMixin

logger = logging.getLogger(__name__)


class FetchLogSheetsByYear(LoginRequiredMixin, IsBowHuntMixin, AJAXResponseMixin, TemplateView):
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
                        'deer': [{'str': deer.as_str, 'tracking': deer.tracking} for deer in log.deer_set.all()],
                        'name': escape(log.hunter.name),
                        'warnings': serializers.serialize(
                            'json', list(log.missing_warnings.all()) + list(log.incorrect_warnings.all())
                        )
                    }
                elif hasattr(log, 'nonhunter'):
                    # Even though information is not really a hunter, we'll add it so that the web page displays the
                    # information in the correct place
                    hunter = {
                        'comment': '',
                        'deer': [{'str': deer.as_str, 'tracking': deer.tracking} for deer in log.deer_set.all()],
                        'name': log.nonhunter.description,
                        'warnings': []
                    }
                else:
                    hunter = None

                if log.location != prev_location:
                    # First time for this location
                    log_data.append({
                        'hunters': None if hunter is None else [hunter],
                        'loc_index': log.location.line_number,
                        'location': log.location.address
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


class LogSheetView(LoginRequiredMixin, IsBowHuntMixin, TemplateView):
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
