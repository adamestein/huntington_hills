from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.edit import ProcessFormView

from ..forms import HunterAnalysisForm
from ..models import Hunter, Log

from library.contrib.auth.mixins import IsBowHuntMixin


class Report(LoginRequiredMixin, IsBowHuntMixin, ProcessFormView, TemplateView):
    request = None
    template_name = 'bow_hunt/reports/by_hunter.html'

    def post(self, request, *args, **kwargs):
        self.request = request

        context = {
            'summary': self._create_summary(**kwargs)
        }

        return self.render_to_response(context)

    @staticmethod
    def _create_summary(**kwargs):
        logs_of_interest = Log.objects.filter(hunter__in=kwargs['hunters'], log_sheet__date__year__in=kwargs['years'])

        summary = {
            'number_hunters': len(kwargs['hunters']),
            'total_hunters': Hunter.objects.exclude(first_name='<unknown>').count(),
            'years': ', '.join(kwargs['years'])
        }

        from ..models import Location

        if HunterAnalysisForm.HUNTER_ANALYSIS_LOCATIONS in kwargs['options']:
            summary['locations'] = logs_of_interest.distinct().values_list('location').count()
            summary['deer_shot'] = logs_of_interest\
                .exclude(deer_count=0)\
                .distinct()\
                .values_list('location')\
                .count()

        if HunterAnalysisForm.HUNTER_ANALYSIS_SUCCESS_RATE in kwargs['options']:
            summary['required_tracking'] = logs_of_interest.filter(deer_tracking=True).count()

        if HunterAnalysisForm.HUNTER_ANALYSIS_TIMES_HUNTED in kwargs['options']:
            summary.update({
                'total_days_hunted': logs_of_interest.distinct().values_list('log_sheet').count(),
                'total_shots_taken': logs_of_interest.exclude(deer_count=0).count()
            })

        return summary

    