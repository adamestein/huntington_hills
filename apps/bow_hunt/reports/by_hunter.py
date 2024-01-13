from django.db.models import Q

from .base import ReportBase
from ..models import Hunter, Log, Site


class Report(ReportBase):
    template_name = 'bow_hunt/reports/by_hunter.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_deer_shot = 0

    def post(self, request, *args, **kwargs):
        query = Q(log_sheet__date__year__in=kwargs['years']) | Q(log_sheet_non_ipd__date__year__in=kwargs['years'])
        self.logs = Log.objects.filter(query, hunter__in=kwargs['hunters'])
        super().post(request, *args, **kwargs)

        context = self.get_context_data(**kwargs)

        # Because some deer are shot by unknown hunters, we need to count using the full Log, not just the
        # filtered version
        query = Q(log_sheet__date__year__in=kwargs['years']) | Q(log_sheet_non_ipd__date__year__in=kwargs['years'])
        self.total_deer_shot = self.deer_count(Log.objects.filter(query))

        hunter_details, hunter_summaries = self._create_hunter_summaries(**kwargs)

        context.update({
            'hunter_details': hunter_details,
            'hunter_summaries': hunter_summaries,
            'log_sheet_ipd_count': Log.objects.filter(log_sheet__date__year__in=kwargs['years']).count(),
            'log_sheet_non_ipd_count': Log.objects.filter(log_sheet_non_ipd__date__year__in=kwargs['years']).count(),
            'summary': self._create_summary(**kwargs)
        })

        return self.render_to_response(context)

    def _create_hunter_summaries(self, **kwargs):
        details = {}
        summaries = {}

        for year in kwargs['years']:
            log_sheet_query = Q(log_sheet__date__year=year) | Q(log_sheet_non_ipd__date__year=year)

            if year not in summaries:
                details[year] = {}
                summaries[year] = {}

            for hunter in Hunter.objects.filter(id__in=kwargs['hunters']):
                hunter_logs = self.logs.filter(log_sheet_query, hunter=hunter)
                hunter_name = str(hunter)

                summary_days_hunted = hunter_logs.distinct().values_list('log_sheet', 'log_sheet_non_ipd').count()
                summary_deer_shot = self.deer_count(hunter_logs)
                summary_deer_tracked = hunter_logs.filter(deer__tracking=True).count()
                summary_percent_shot = summary_deer_shot / self.total_deer_shot * 100 if self.total_deer_shot else 0
                summary_per_tracked = summary_deer_tracked / summary_deer_shot * 100 if summary_deer_shot else 0

                hunter_sites = Site.objects.filter(
                    id__in=hunter_logs.distinct().values_list('location__site', flat=True).order_by('location__site')
                )

                summaries[year][hunter_name] = {
                    'days_hunted': summary_days_hunted,
                    'deer_shot': summary_deer_shot,
                    'deer_tracked': summary_deer_tracked,
                    'locations_hunted': hunter_sites.count(),
                    'percent_shot': summary_percent_shot,
                    'percent_tracked': summary_per_tracked
                }

                details[year][hunter_name] = {'normalized_name': hunter.name}

                for site in hunter_sites:
                    location_logs = hunter_logs.filter(location__site=site)

                    if location_logs:
                        location = str(location_logs[0].location.site)

                        detailed_days_hunted = location_logs.count()
                        detailed_deer_shot = self.deer_count(location_logs)
                        detailed_deer_tracked = location_logs.filter(deer__tracking=True).count()
                        detailed_percent_deer_shot = detailed_deer_shot / summary_deer_shot * 100 \
                            if summary_deer_shot else 0
                        detailed_percent_tracked = detailed_deer_tracked / detailed_deer_shot * 100 \
                            if detailed_deer_shot else 0

                        details[year][hunter_name][location] = {
                            'days_hunted': detailed_days_hunted,
                            'deer_shot': detailed_deer_shot,
                            'deer_tracked': detailed_deer_tracked,
                            'percent_days_hunted': detailed_days_hunted / summary_days_hunted * 100,
                            'percent_shot': detailed_percent_deer_shot,
                            'percent_tracked': detailed_percent_tracked
                        }

        return details, summaries

    def _create_summary(self, **kwargs):
        return {
            'locations': self.logs.distinct().values_list('location').count(),
            'number_locs_deer_shot': self.logs.exclude(deer__isnull=True).distinct().values_list('location').count(),
            'number_hunters': len(kwargs['hunters']),
            'required_tracking': self.logs.filter(deer__tracking=True).count(),
            'total_days_hunted': self.logs.distinct().values_list('log_sheet', 'log_sheet_non_ipd').count(),
            'total_deer_shot': self.total_deer_shot,
            'total_hunters': Hunter.objects.exclude(first_name='<unknown>').count(),
            'years': self.get_year_info(**kwargs)
        }


    