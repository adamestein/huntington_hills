from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .models import HHCommonsHunting


class CommonsHunting(LoginRequiredMixin, TemplateView):
    template_name = 'bow_hunt/commons_hunting.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exceptions'] = HHCommonsHunting.objects.all()
        return context
