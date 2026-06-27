from io import BytesIO
from os import path
from urllib.parse import quote

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.generic.base import ContextMixin, View
from xhtml2pdf import pisa


def _fetch_resources(uri, rel):
    if settings.STATIC_URL and uri.startswith(settings.STATIC_URL):
        resource_path = path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ''))
    elif settings.MEDIA_URL and uri.startswith(settings.MEDIA_URL):
        resource_path = path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
    else:
        resource_path = path.join(settings.STATIC_ROOT, uri)

    return resource_path.replace('\\', '/')


def _content_disposition_filename(filename):
    quoted = quote(filename)
    if quoted == filename:
        return f'filename={filename}'
    return f"filename*=UTF-8''{quoted}"


class PDFTemplateView(ContextMixin, View):
    pdf_filename = None
    template_name = None

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        html = render_to_string(self.template_name, context, request=request)

        src = BytesIO(html.encode('utf-8'))
        dest = BytesIO()
        pdf = pisa.pisaDocument(src, dest, encoding='utf-8', link_callback=_fetch_resources)

        if pdf.err:
            return HttpResponse('Error rendering PDF', status=500)

        response = HttpResponse(dest.getvalue(), content_type='application/pdf')
        if self.pdf_filename:
            response['Content-Disposition'] = f'attachment; {_content_disposition_filename(self.pdf_filename)}'
        return response
