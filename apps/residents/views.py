from django.views.generic.base import TemplateView

from .models import Property, Street


class ResidentListView(TemplateView):
    template_name = 'residents/residents.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['properties'] = Property.objects.all()
        context['by_street'] = {}

        for street in Street.objects.all():
            context['by_street'][street.street] = Property.objects.filter(street=street)

        return context
