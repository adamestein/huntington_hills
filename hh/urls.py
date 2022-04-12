"""hh URL Configuration
"""

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import reverse_lazy
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(url=reverse_lazy('login'), permanent=True)),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^auth/', include('authentication.urls')),
    url(r'^bow_hunt/', include('bow_hunt.urls')),
    url(r'^gallery/', include('gallery.urls')),
    url(r'^news/', include('news.urls')),
    url(r'^resident/', include('residents.urls')),
    url(r'^staff/', include('staff.urls')),
    url(r'^tinymce/', include('tinymce.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
