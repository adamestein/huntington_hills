from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.views.generic import TemplateView
from django.views.generic.edit import ProcessFormView

from ..models import LogSheet

from library.contrib.auth.mixins import IsBowHuntMixin


class ReportBase(LoginRequiredMixin, IsBowHuntMixin, ProcessFormView, TemplateView):
    logs = None
    request = None
    template_name = None

    @staticmethod
    def deer_count(query):
        return query.exclude(deer__isnull=True).aggregate(deer_count=Coalesce(Sum('deer__count'), 0))['deer_count']

    def get_context_data(self, **kwargs):
        has_incorrect_warnings = self.logs.exclude(incorrect_warnings=None).count() > 0
        has_missing_warnings = self.logs.exclude(missing_warnings=None).count() > 0

        # Now that we have warning information, we can remove anything where the listed hunter wasn't actually there
        self.logs = self.logs.exclude(incorrect_warnings__label='Listed hunter didn\'t actually hunt here')

        return {
            'has_incorrect_warnings': has_incorrect_warnings,
            'has_missing_warnings': has_missing_warnings
        }

    @staticmethod
    def get_year_info(**kwargs):
        years = {}
        for year in kwargs['years']:
            years[year] = LogSheet.objects.filter(date__year=year).count()
        return years

    def post(self, request, *args, **kwargs):
        self.request = request
