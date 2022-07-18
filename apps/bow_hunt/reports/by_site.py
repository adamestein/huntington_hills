from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max, Min
from django.views.generic import TemplateView
from django.views.generic.edit import ProcessFormView

from ..models import Log, Site

from library.contrib.auth.mixins import IsBowHuntMixin
from library.query import median_value


class Report(LoginRequiredMixin, IsBowHuntMixin, ProcessFormView, TemplateView):
    request = None
    sites = []
    template_name = 'bow_hunt/reports/by_site.html'

    def post(self, request, *args, **kwargs):
        self.request = request
        self.sites = Site.objects.filter(
            id__in=[site.id for site in Site.objects.all() if str(site) in kwargs['sites']]
        )

        for site in self.sites:
            site.hunted_on = Log.objects.filter(
                location__in=site.location_set.all()
            ).exclude(hunter__isnull=True).count()

        context = {
            'sites': self.sites,
            'summary': self._create_summary()
        }

        return self.render_to_response(context)

    def _create_summary(self):
        return {
            'maximum_size': self.sites.aggregate(Max('acres'))['acres__max'],
            'median_size': median_value(self.sites, 'acres'),
            'minimum_size': self.sites.aggregate(Min('acres'))['acres__min'],
            'number_locations': len(self.sites),
            'total_locations': Site.objects.all().count()
        }
