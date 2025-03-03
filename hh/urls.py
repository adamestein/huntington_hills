"""hh URL Configuration
"""

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.views.generic import TemplateView

from library.views.generic import ProtectedMedia

urlpatterns = (
    [
        url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
        url(r'^about/$', TemplateView.as_view(template_name='about.html'), name='about'),
        url(r'^accounts/', include('django.contrib.auth.urls')),
        url(r'^admin/', admin.site.urls),
        url(r'^auth/', include('authentication.urls')),
        url(r'^bow_hunt/', include('bow_hunt.urls')),
        url(r'^contact/', include('contact.urls')),
        url(r'^docs/', include('docs.urls')),
        url(r'^gallery/', include('gallery.urls')),
        url(r'^history/', include('history.urls')),
        url(r'^mailing_lists/', include('mailing_lists.urls')),
        url(r'^media/members/(?:.*)$', ProtectedMedia.as_view(), name='media'),
        url(r'^news/', include('news.urls')),
        url(r'^resident/', include('residents.urls')),
        url(r'^search/$', TemplateView.as_view(template_name='search.html'), name='search'),
        url(r'^staff/', include('staff.urls')),
        url(r'^technical/$', TemplateView.as_view(template_name='technical.html'), name='technical'),
        url(r'^tinymce/', include('tinymce.urls'))
    ] +
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +
    static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
