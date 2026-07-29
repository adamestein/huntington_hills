import pytest
from django.urls import reverse

from gallery.models import Owner


@pytest.fixture
def owner(db):
    return Owner.objects.create(name='Test Owner')


class TestGalleryPage:
    def test_page_loads(self, page, live_server):
        page.goto(f'{live_server.url}{reverse("gallery:gallery")}')
        assert page.locator('#header h1').text_content() == 'Gallery'

    def test_shows_no_photos_when_empty(self, page, live_server):
        page.goto(f'{live_server.url}{reverse("gallery:gallery")}')
        assert page.locator('text=There are currently no photographs online at this time.').is_visible()

    def test_shows_owner_list(self, page, live_server, owner):
        page.goto(f'{live_server.url}{reverse("gallery:gallery")}')
        owner_section = page.locator('#left')
        assert owner_section.locator(f'text={owner.name}').is_visible()

    def test_owner_is_link(self, page, live_server, owner):
        page.goto(f'{live_server.url}{reverse("gallery:gallery")}')
        owner_link = page.locator(f'a[href="{reverse("gallery:owner", kwargs={"slug": owner.slug})}"]')
        assert owner_link.is_visible()

    def test_footer_links_exist(self, page, live_server):
        page.goto(f'{live_server.url}{reverse("gallery:gallery")}')
        home_link = page.locator(f'a[href="{reverse("home")}"]')
        assert home_link.is_visible()


class TestOwnerPage:
    def test_page_loads(self, page, live_server, owner):
        page.goto(f'{live_server.url}{reverse("gallery:owner", kwargs={"slug": owner.slug})}')
        assert page.locator('#header h1').text_content() == 'Gallery'

    def test_shows_owner_name(self, page, live_server, owner):
        page.goto(f'{live_server.url}{reverse("gallery:owner", kwargs={"slug": owner.slug})}')
        owner_entry = page.locator('#left li')
        assert owner_entry.locator(f'text={owner.name}').is_visible()

    def test_shows_owner_in_right(self, page, live_server, owner):
        page.goto(f'{live_server.url}{reverse("gallery:owner", kwargs={"slug": owner.slug})}')
        right = page.locator('#right')
        assert right.locator(f'text={owner.name}').is_visible()
