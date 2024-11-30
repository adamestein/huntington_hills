from mimetypes import MimeTypes
import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, HttpResponseNotFound
from django.views.generic import View


class ProtectedMedia(LoginRequiredMixin, View):
    @staticmethod
    def get(request, *args, **kwargs):
        absolute_path = __file__.replace('/apps/library/views/generic/media.py', request.get_full_path())

        if os.path.exists(absolute_path):
            mime = MimeTypes()
            content_type, encoding = mime.guess_type(absolute_path)

            if content_type is None:
                content_type = 'application/octet-stream'

            response = FileResponse(open(absolute_path, 'rb'), content_type=content_type)
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(absolute_path)}"'
            return response
        else:
            return HttpResponseNotFound('file not found')
