import pytest
from django.urls import reverse


class TestContactPage:
    def test_page_loads(self, page, live_server):
        page.goto(f'{live_server.url}{reverse("contact:contact")}')
        assert page.locator('h1').text_content() == 'Contact'

    def test_has_board_link(self, page, live_server):
        page.goto(f'{live_server.url}{reverse("contact:contact")}')
        board_link = page.locator(f'a[href="{reverse("contact:board")}"]')
        assert board_link.is_visible()

    def test_has_adam_link(self, page, live_server):
        page.goto(f'{live_server.url}{reverse("contact:contact")}')
        adam_link = page.locator(f'a[href="{reverse("contact:adam")}"]')
        assert adam_link.is_visible()

    def test_has_webmaster_link(self, page, live_server):
        page.goto(f'{live_server.url}{reverse("contact:contact")}')
        webmaster_link = page.locator(f'a[href="{reverse("contact:webmaster")}"]')
        assert webmaster_link.is_visible()


class TestContactForm:
    RECIPIENTS = [
        ('adam', 'Adam Stein'),
        ('board', 'Board'),
        ('webmaster', 'Webmaster'),
    ]

    @pytest.mark.parametrize('url_name,recipient', RECIPIENTS)
    def test_form_page_loads(self, page, live_server, url_name, recipient):
        page.goto(f'{live_server.url}{reverse(f"contact:{url_name}")}')
        assert page.locator('h1').text_content() == f'Email Form: {recipient}'

    @pytest.mark.parametrize('url_name,_', RECIPIENTS)
    def test_form_has_fields(self, page, live_server, url_name, _):
        page.goto(f'{live_server.url}{reverse(f"contact:{url_name}")}')
        assert page.locator('#id_name').is_visible()
        assert page.locator('#id_email').is_visible()
        assert page.locator('#id_message').is_visible()

    @pytest.mark.parametrize('url_name,_', RECIPIENTS)
    def test_form_has_submit_button(self, page, live_server, url_name, _):
        page.goto(f'{live_server.url}{reverse(f"contact:{url_name}")}')
        assert page.locator('input[type="submit"]').is_visible()
