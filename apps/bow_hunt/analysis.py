from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView

from .forms import HunterAnalysisForm, LocationAnalysisForm
from .reports.by_hunter import Report as ReportByHunter
from .reports.by_location import Report as ReportByLocation

from library.contrib.auth.mixins import IsBowHuntMixin


class HunterAnalysis(LoginRequiredMixin, IsBowHuntMixin, FormView):
    form_class = HunterAnalysisForm
    template_name = 'bow_hunt/hunter_analysis.html'

    def form_valid(self, form):
        return ReportByHunter().post(self.request, **form.cleaned_data)


class LocationAnalysis(LoginRequiredMixin, IsBowHuntMixin, FormView):
    form_class = LocationAnalysisForm
    template_name = 'bow_hunt/location_analysis.html'

    def form_valid(self, form):
        return ReportByLocation().post(self.request, **form.cleaned_data)
