import json

from django.http import HttpResponse
from django.views.generic.base import TemplateResponseMixin


class AJAXResponseMixin(TemplateResponseMixin):
    def post(self, request, *args, **kwargs):
        # noinspection PyUnresolvedReferences
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response, using the `response_class` for this
        view, with a template rendered with the given context.

        If any keyword arguments are provided, they will be
        passed to the constructor of the response class.
        """
        response_kwargs.setdefault('content_type', self.content_type)
        return HttpResponse(json.dumps(context))
