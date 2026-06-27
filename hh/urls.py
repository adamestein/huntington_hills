"""hh URL Configuration
"""

from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import include, re_path
from django.views.generic import TemplateView

from library.views.generic import ProtectedMedia

urlpatterns = ([
    re_path(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    re_path(r'^about/$', TemplateView.as_view(template_name='about.html'), name='about'),
    re_path(r'^accounts/', include('django.contrib.auth.urls')),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^auth/', include('authentication.urls')),
    re_path(r'^bow_hunt/', include('bow_hunt.urls')),
    re_path(r'^contact/', include('contact.urls')),
    re_path(r'^docs/', include('docs.urls')),
    re_path(r'^gallery/', include('gallery.urls')),
    re_path(r'^history/', include('history.urls')),
    re_path(r'^mailing_lists/', include('mailing_lists.urls')),
    re_path(r'^media/members/(?:.*)$', ProtectedMedia.as_view(), name='media'),
    re_path(r'^news/', include('news.urls')),
    re_path(r'^resident/', include('residents.urls')),
    re_path(r'^search/$', TemplateView.as_view(template_name='search.html'), name='search'),
    re_path(r'^staff/', include('staff.urls')),
    re_path(r'^technical/$', TemplateView.as_view(template_name='technical.html'), name='technical'),
    re_path(r'^tinymce/', include('tinymce.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
