from django.db.models import Q

from .base import ReportBase
from ..models import Log, Site


class Report(ReportBase):
    template_name = 'bow_hunt/reports/by_location.html'
    years = None

    def post(self, request, *args, **kwargs):
        query = Q(log_sheet__date__year__in=kwargs['years']) | Q(log_sheet_non_ipd__date__year__in=kwargs['years'])
        self.logs = Log.objects.filter(query, location__label__in=kwargs['locations']).exclude(hunter__isnull=True)

        super().post(request, *args, **kwargs)

        self.years = self.get_year_info(**kwargs)

        context = self.get_context_data(**kwargs)

        location_details, location_summaries = self._create_location_summaries(**kwargs)

        context.update({
            'location_details': location_details,
            'location_summaries': location_summaries,
            'log_sheet_ipd_count': Log.objects.filter(log_sheet__date__year__in=kwargs['years']).count(),
            'log_sheet_non_ipd_count': Log.objects.filter(log_sheet_non_ipd__date__year__in=kwargs['years']).count(),
            'summary': self._create_summary(**kwargs)
        })

        return self.render_to_response(context)

    def _create_location_summaries(self, **kwargs):
        details = {}
        summaries = {}

        for year in kwargs['years']:
            query = Q(log_sheet__date__year=year) | Q(log_sheet_non_ipd__date__year=year)

            if year not in summaries:
                details[year] = {}
                summaries[year] = {}

            # Because some deer are shot by unknown hunters, we need to count using the full Log, not just the
            # filtered version
            total_deer_shot = self.deer_count(Log.objects.filter(query))

            for location in self.sites:
                location_logs = self.logs.filter(query, location__site=location)

                summary_days_hunted = location_logs.distinct().values('log_sheet__date').count()
                summary_deer_shot = self.deer_count(location_logs)
                summary_deer_tracked = location_logs.filter(deer__tracking=True).count()
                summary_percent_shot = summary_deer_shot / total_deer_shot * 100 if total_deer_shot else 0
                summary_per_tracked = summary_deer_tracked / summary_deer_shot * 100 if summary_deer_shot else 0

                summaries[year][location] = {
                    'days_hunted': summary_days_hunted,
                    'deer_shot': summary_deer_shot,
                    'deer_tracked': summary_deer_tracked,
                    'percent_hunted': summary_days_hunted / self.years[year] * 100 if self.years[year] else 0,
                    'percent_shot': summary_percent_shot,
                    'percent_tracked': summary_per_tracked
                }

                details[year][location] = {}
                hunter_ids = location_logs\
                    .exclude(hunter__first_name='<unknown>')\
                    .distinct()\
                    .values_list('hunter', flat=True)\
                    .order_by('hunter')

                for hunter_id in hunter_ids:
                    hunter_logs = location_logs.filter(hunter_id=hunter_id)

                    if hunter_logs:
                        hunter = hunter_logs[0].hunter
                        hunter_name = str(hunter)

                        details_days_hunted = hunter_logs.count()
                        detailed_deer_shot = self.deer_count(hunter_logs)
                        detailed_deer_tracked = hunter_logs.filter(deer__tracking=True).count()
                        detailed_percent_deer_shot = detailed_deer_shot / summary_deer_shot * 100 \
                            if summary_deer_shot else 0
                        detailed_percent_tracked = detailed_deer_tracked / detailed_deer_shot * 100 \
                            if detailed_deer_shot else 0

                        details[year][location][hunter_name] = {
                            'days_hunted': details_days_hunted,
                            'deer_shot': detailed_deer_shot,
                            'deer_tracked': detailed_deer_tracked,
                            'percent_days_hunted': details_days_hunted / summary_days_hunted * 100,
                            'percent_shot': detailed_percent_deer_shot,
                            'percent_tracked': detailed_percent_tracked
                        }

        return details, summaries

    def _create_summary(self, **kwargs):
        return {
            'number_locations': len(kwargs['locations']),
            'required_tracking': self.logs.filter(deer__tracking=True).count(),
            'total_days_hunted': self.logs.exclude(hunter__isnull=True).count(),
            'total_deer_shot': self.deer_count(self.logs),
            'total_locations': Site.objects.all().count(),
            'years': self.years
        }


    