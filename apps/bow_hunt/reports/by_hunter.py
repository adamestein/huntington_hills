from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.edit import ProcessFormView

from ..forms import HunterAnalysisForm
from ..models import Hunter, Log, LogSheet

from library.contrib.auth.mixins import IsBowHuntMixin


class Report(LoginRequiredMixin, IsBowHuntMixin, ProcessFormView, TemplateView):
    logs = None
    request = None
    template_name = 'bow_hunt/reports/by_hunter.html'

    def post(self, request, *args, **kwargs):
        self.logs = Log.objects.filter(hunter__in=kwargs['hunters'], log_sheet__date__year__in=kwargs['years'])
        self.request = request

        hunter_details, hunter_summaries = self._create_hunter_summaries(**kwargs)

        context = {
            'has_incorrect_warnings': self.logs.exclude(incorrect_warnings=None).count() > 0,
            'has_missing_warnings': self.logs.exclude(missing_warnings=None).count() > 0,
            'hunter_details': hunter_details,
            'hunter_summaries': hunter_summaries,
            'summary': self._create_summary(**kwargs)
        }

        return self.render_to_response(context)

    def _create_hunter_summaries(self, **kwargs):
        details = {}
        summaries = {}

        for year in kwargs['years']:
            if year not in summaries:
                details[year] = {}
                summaries[year] = {}

            for hunter in Hunter.objects.filter(id__in=kwargs['hunters']):
                hunter_logs = self.logs\
                    .filter(hunter=hunter)\
                    .exclude(incorrect_warnings__label='Listed hunter didn\'t actually hunt here')
                hunter_name = str(hunter)

                summary_days_hunted = hunter_logs.distinct().values_list('log_sheet').count()
                summary_deer_shot = hunter_logs.exclude(deer__isnull=True).count()
                summary_deer_tracked = hunter_logs.filter(deer__tracking=True).count()
                summary_percent_shot = summary_deer_shot / summary_days_hunted * 100
                summary_per_tracked = 0 if summary_deer_shot == 0 else summary_deer_tracked / summary_deer_shot * 100

                summaries[year][hunter_name] = {
                    'days_hunted': summary_days_hunted,
                    'deer_shot': summary_deer_shot,
                    'deer_tracked': summary_deer_tracked,
                    'locations_hunted': hunter_logs.distinct().values_list('location').count(),
                    'percent_shot': summary_percent_shot,
                    'percent_tracked': summary_per_tracked
                }

                details[year][hunter_name] = {}

                for location_id in hunter_logs.distinct().values_list('location', flat=True):
                    location_logs = hunter_logs.filter(location_id=location_id)

                    if location_logs:
                        location = location_logs[0].location.address

                        location_days_hunted = location_logs.count()
                        location_deer_shot = location_logs.exclude(deer__isnull=True).count()
                        location_deer_tracked = location_logs.filter(deer__tracking=True).count()
                        loc_per_deer_shot = 0 if summary_deer_shot == 0 else location_deer_shot / summary_deer_shot * 100
                        loc_per_tracked = 0 if location_deer_shot == 0 else location_deer_tracked / location_deer_shot * 100

                        details[year][hunter_name][location] = {
                            'days_hunted': location_days_hunted,
                            'percent_days_hunted': location_days_hunted / summary_days_hunted * 100,
                            'deer_shot': location_deer_shot,
                            'deer_tracked': location_deer_tracked,
                            'percent_shot': loc_per_deer_shot,
                            'percent_tracked': loc_per_tracked
                        }

        return details, summaries

    def _create_summary(self, **kwargs):
        years = {}
        for year in kwargs['years']:
            years[year] = LogSheet.objects.filter(date__year=year).count()

        summary = {
            'locations': self.logs.distinct().values_list('location').count(),
            'number_locs_deer_shot': self.logs.exclude(deer__isnull=True).distinct().values_list('location').count(),
            'number_hunters': len(kwargs['hunters']),
            'required_tracking': self.logs.filter(deer__tracking=True).count(),
            'total_days_hunted': self.logs.distinct().values_list('log_sheet').count(),
            'total_deer_shot': self.logs.exclude(deer__isnull=True).count(),
            'total_hunters': Hunter.objects.exclude(first_name='<unknown>').count(),
            'years': years
        }

        return summary

    