from django.db.models import Sum
from django.db.models.functions import Coalesce

from .base import ReportBase
from ..models import Location, Log


class Report(ReportBase):
    template_name = 'bow_hunt/reports/by_location.html'
    years = None

    def post(self, request, *args, **kwargs):
        self.logs = Log.objects\
            .filter(location__address__in=kwargs['locations'], log_sheet__date__year__in=kwargs['years'])\
            .exclude(hunter__isnull=True)
        super().post(request, *args, **kwargs)

        self.years = self.get_year_info(**kwargs)

        context = self.get_context_data(**kwargs)

        location_details, location_summaries = self._create_location_summaries(**kwargs)

        context.update({
            'location_details': location_details,
            'location_summaries': location_summaries,
            'summary': self._create_summary(**kwargs)
        })

        return self.render_to_response(context)

    def _create_location_summaries(self, **kwargs):
        details = {}
        summaries = {}

        for year in kwargs['years']:
            if year not in summaries:
                details[year] = {}
                summaries[year] = {}

            # Because some deer are shot by unknown hunters, we need to count using the full Log, not just the
            # filtered version
            total_deer_shot = self.deer_count(Log.objects.filter(log_sheet__date__year=year))

            for location in kwargs['locations']:
                location_logs = self.logs.filter(location__address=location, log_sheet__date__year=year)

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


            # for hunter in Hunter.objects.filter(id__in=kwargs['hunters']):
            #     details[year][hunter_name] = {}
            #
            #     for location_id in hunter_logs.distinct().values_list('location', flat=True):
            #         location_logs = hunter_logs.filter(location_id=location_id)
            #
            #         if location_logs:
            #             location = location_logs[0].location.address
            #
            #             location_days_hunted = location_logs.count()
            #             location_deer_shot = self._count_deer(location_logs)
            #             location_deer_tracked = location_logs.filter(deer__tracking=True).count()
            #             location_percent_deer_shot = location_deer_shot / summary_deer_shot * 100 \
            #                 if summary_deer_shot else 0
            #             location_percent_tracked = location_deer_tracked / location_deer_shot * 100 \
            #                 if location_deer_shot else 0
            #
            #             details[year][hunter_name][location] = {
            #                 'days_hunted': location_days_hunted,
            #                 'percent_days_hunted': location_days_hunted / summary_days_hunted * 100,
            #                 'deer_shot': location_deer_shot,
            #                 'deer_tracked': location_deer_tracked,
            #                 'percent_shot': location_percent_deer_shot,
            #                 'percent_tracked': location_percent_tracked
            #             }

        return details, summaries

    def _create_summary(self, **kwargs):
        summary = {
            'number_locations': len(kwargs['locations']),
            'required_tracking': self.logs.filter(deer__tracking=True).count(),
            'total_days_hunted': self.logs.exclude(hunter__isnull=True).count(),
            'total_deer_shot': self.deer_count(self.logs),
            'total_locations': Location.objects.distinct().values('address').count(),
            'years': self.years
        }

        return summary

    