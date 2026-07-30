"""hh URL Configuration
"""

from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import include, path, re_path
from django.views.generic import TemplateView

from library.views.generic import ProtectedMedia

urlpatterns = ([
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('bow_hunt/', include('bow_hunt.urls')),
    path('contact/', include('contact.urls')),
    path('docs/', include('docs.urls')),
    path('gallery/', include('gallery.urls')),
    path('history/', include('history.urls')),
    path('mailing_lists/', include('mailing_lists.urls')),
    re_path(r'^media/members/(?:.*)$', ProtectedMedia.as_view(), name='media'),
    path('news/', include('news.urls')),
    path('resident/', include('residents.urls')),
    path('search/', TemplateView.as_view(template_name='search.html'), name='search'),
    path('staff/', include('staff.urls')),
    path('technical/', TemplateView.as_view(template_name='technical.html'), name='technical'),
    path('tinymce/', include('tinymce.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
