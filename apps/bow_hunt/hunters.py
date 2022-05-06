from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView

from .forms import HunterAnalysisForm
from .reports.by_hunter import Report

from library.contrib.auth.mixins import IsBowHuntMixin


class HunterAnalysis(LoginRequiredMixin, IsBowHuntMixin, FormView):
    form_class = HunterAnalysisForm
    template_name = 'bow_hunt/hunter_analysis.html'

    def form_valid(self, form):
        return Report().post(self.request, **form.cleaned_data)
