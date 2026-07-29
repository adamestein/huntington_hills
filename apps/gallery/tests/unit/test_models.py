from io import BytesIO

from PIL import Image

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

import pytest

from gallery.models import Owner, Photo, TNAIL_BACKGROUND_HEIGHT, TNAIL_BACKGROUND_WIDTH


@pytest.fixture
def owner(db):
    return Owner.objects.create(name='Test Owner')


@pytest.fixture
def owner_unicode(db):
    return Owner.objects.create(name='Frédéric Müller')


@pytest.fixture
def photo_image():
    img = Image.new('RGB', (200, 150), color='red')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    return ContentFile(buffer.getvalue(), name='test.jpg')


@pytest.fixture
def photo(db, owner, photo_image):
    return Photo.objects.create(
        owner=owner,
        page=1,
        short_description='A test photo',
        image=photo_image,
    )


@pytest.mark.django_db
class TestOwnerStr:
    def test_str(self, owner):
        assert str(owner) == 'Test Owner'

    def test_str_unicode(self, owner_unicode):
        assert str(owner_unicode) == 'Frédéric Müller'


@pytest.mark.django_db
class TestOwnerSlug:
    def test_slug_set_on_save(self, owner):
        assert owner.slug == 'test-owner'

    def test_slug_unicode(self, owner_unicode):
        assert owner_unicode.slug == 'frederic-muller'


@pytest.mark.django_db
class TestOwnerNumPages:
    def test_no_photos(self, owner):
        assert owner.num_pages == 0

    def test_single_page(self, db, owner, photo_image):
        Photo.objects.create(owner=owner, page=1, short_description='Photo 1', image=photo_image)
        assert owner.num_pages == 1

    def test_multiple_pages(self, db, owner, photo_image):
        Photo.objects.create(owner=owner, page=1, short_description='Photo 1', image=photo_image)
        Photo.objects.create(owner=owner, page=2, short_description='Photo 2', image=photo_image)
        assert owner.num_pages == 2

    def test_duplicate_pages_deduped(self, db, owner, photo_image):
        Photo.objects.create(owner=owner, page=1, short_description='Photo A', image=photo_image)
        Photo.objects.create(owner=owner, page=1, short_description='Photo B', image=photo_image)
        assert owner.num_pages == 1


@pytest.mark.django_db
class TestPhotoStr:
    def test_str(self, photo):
        assert str(photo) == '[Test Owner/1] A test photo'


@pytest.mark.django_db
class TestPhotoTnailMarginTop:
    def test_margin_top(self, photo):
        expected = int(TNAIL_BACKGROUND_HEIGHT / 2 - photo.tnail_height / 2)
        assert photo.tnail_margin_top == expected

    def test_zero_height(self, db, owner, photo_image):
        photo = Photo.objects.create(
            owner=owner, page=1, short_description='Zero',
            image=photo_image,
        )
        photo.tnail_height = 0
        expected = int(TNAIL_BACKGROUND_HEIGHT / 2)
        assert photo.tnail_margin_top == expected


@pytest.mark.django_db
class TestPhotoOwnerOrdering:
    def test_owner_ordering(self, db, owner):
        assert Photo._meta.ordering == ('owner', 'page', 'image')


@pytest.mark.django_db
class TestOwnerOrdering:
    def test_owner_ordering(self):
        assert Owner._meta.ordering == ('name',)
