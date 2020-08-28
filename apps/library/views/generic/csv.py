import csv

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.views.generic.base import ContextMixin, View


class CSVResponseMixin(object):
    content_type = None
    csv_filename = None

    def render_to_response(self, context):
        response = HttpResponse(content_type=self.content_type)
        response['Content-Disposition'] = f'attachment; filename="{self.csv_filename}"'

        writer = csv.writer(response)

        data = context.get('data')
        if data is None:
            raise ImproperlyConfigured("CSVResponseMixin requires 'data' to be set in the context")

        for row in data:
            writer.writerow(row)

        return response


class CSVFileView(CSVResponseMixin, ContextMixin, View):
    content_type = 'text/csv'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
