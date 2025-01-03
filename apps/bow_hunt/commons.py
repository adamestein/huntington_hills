from library.views.generic import ProtectedTemplateView

from .models import HHCommonsHunting


class CommonsHunting(ProtectedTemplateView):
    template_name = 'bow_hunt/commons_hunting.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exceptions'] = HHCommonsHunting.objects.all()
        return context
