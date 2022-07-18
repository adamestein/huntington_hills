from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView

from .forms import HunterAnalysisForm, LocationAnalysisForm, SiteAnalysisForm
from .reports.by_hunter import Report as ReportByHunter
from .reports.by_location import Report as ReportByLocation
from .reports.by_site import Report as ReportBySite

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


class SiteAnalysis(LoginRequiredMixin, IsBowHuntMixin, FormView):
    form_class = SiteAnalysisForm
    template_name = 'bow_hunt/site_analysis.html'

    def form_valid(self, form):
        return ReportBySite().post(self.request, **form.cleaned_data)
