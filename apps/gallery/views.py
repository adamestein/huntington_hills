from django.views.generic import DetailView, ListView

from .models import TNAIL_BACKGROUND_HEIGHT, TNAIL_BACKGROUND_WIDTH, Owner, Photo


class GalleryView(ListView):
    model = Owner
    template_name = 'gallery/gallery.html'


class OwnerView(DetailView):
    model = Owner
    template_name = 'gallery/owner.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner_list'] = Owner.objects.all()
        context['pages'] = [f'Page {page_num}' for page_num in range(1, self.object.num_pages + 1)]

        return context


class PageView(ListView):
    model = Photo
    template_name = 'gallery/page.html'

    def get_context_data(self, **kwargs):
        owner = Owner.objects.get(slug=self.kwargs['owner_slug'])
        kwargs['object_list'] = Photo.objects.filter(owner=owner)
        context = super().get_context_data(**kwargs)
        context['box_size'] = (TNAIL_BACKGROUND_WIDTH, TNAIL_BACKGROUND_HEIGHT)
        context['object'] = owner
        context['owner_list'] = Owner.objects.all()
        context['page_num'] = self.kwargs['page_num']

        return context
