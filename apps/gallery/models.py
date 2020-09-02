from io import BytesIO
from os import path

from PIL import Image

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify

TNAIL_BACKGROUND_HEIGHT = 119
TNAIL_BACKGROUND_WIDTH = 119


def gallery_path(instance, filename):
    return f'gallery/{instance.owner.slug}/{instance.page}/{filename}'


def gallery_tnail_path(instance, filename):
    return f'gallery/{instance.owner.slug}/{instance.page}/tnail/{filename}'


class Owner(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(editable=False, unique=True)

    @property
    def num_pages(self):
        return self.photo_set.order_by('page').distinct().count()

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(**kwargs)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Photo(models.Model):
    height = models.PositiveIntegerField(editable=False)
    image = models.ImageField(height_field='height', upload_to=gallery_path, width_field='width')
    long_description = models.TextField(blank=True)
    owner = models.ForeignKey('Owner')
    page = models.PositiveSmallIntegerField()
    short_description = models.CharField(blank=True, max_length=80)
    tnail = models.ImageField(
        editable=False, height_field='tnail_height', upload_to=gallery_tnail_path, width_field='tnail_width'
    )
    tnail_height = models.PositiveIntegerField(editable=False)
    tnail_width = models.PositiveIntegerField(editable=False)
    width = models.PositiveIntegerField(editable=False)

    class Meta:
        ordering = ('owner', 'page')

    @property
    def tnail_margin_top(self):
        return int(TNAIL_BACKGROUND_HEIGHT / 2 - self.tnail_height / 2)

    def save(self, **kwargs):
        image = Image.open(self.image if self.pk is None else self.image.path)
        image.thumbnail((TNAIL_BACKGROUND_WIDTH, TNAIL_BACKGROUND_HEIGHT))

        buffer = BytesIO()
        image.save(fp=buffer, format='PNG')
        tnail = ContentFile(buffer.getvalue())
        filename, _ = path.splitext(path.basename(self.image.name))
        filename += '.png'

        self.tnail.save(
            filename,
            InMemoryUploadedFile(
                tnail,              # file
                None,               # field_name
                filename,           # file name
                'image/jpeg',       # content_type
                tnail.tell,         # size
                None                # content_type_extra
            ),
            save=False
        )

        super().save(**kwargs)

    def __str__(self):
        return f'[{self.owner}] {self.short_description}'
