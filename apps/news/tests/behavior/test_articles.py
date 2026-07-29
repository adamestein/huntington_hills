from datetime import date, timedelta

import pytest
from django.urls import reverse
from django.utils.text import slugify

from news.models import Article


@pytest.fixture
def article(db):
    return Article.objects.create(
        title='Test Article',
        short_desc='A short description',
        desc='<p>Full content</p>',
        posted_on=date(2024, 6, 15),
        posted_until=date(2024, 7, 15),
    )


@pytest.fixture
def current_article(db):
    today = date.today()
    return Article.objects.create(
        title='Current Article',
        short_desc='Still active',
        desc='<p>Active content</p>',
        posted_on=today - timedelta(days=5),
        posted_until=today + timedelta(days=5),
    )


class TestNewsArchived:
    def test_page_loads(self, page, live_server):
        page.goto(f'{live_server.url}{reverse("news:archived")}')
        assert page.locator('h1').text_content() == 'Archived News'

    def test_shows_years(self, page, live_server, article):
        page.goto(f'{live_server.url}{reverse("news:archived")}')
        year_link = page.locator(f'a[href*="/news/by_year/{article.posted_on.year}"]')
        assert year_link.is_visible()

    def test_empty_when_no_articles(self, page, live_server):
        page.goto(f'{live_server.url}{reverse("news:archived")}')
        year_links = page.locator('a[href*="/news/by_year/"]')
        assert year_links.count() == 0


class TestNewsByYear:
    def test_page_loads(self, page, live_server, article):
        url = reverse('news:by_year', kwargs={'year': article.posted_on.year})
        page.goto(f'{live_server.url}{url}')
        assert page.locator('h1').text_content() == f'News in {article.posted_on.year}'

    def test_shows_article_date(self, page, live_server, article):
        url = reverse('news:by_year', kwargs={'year': article.posted_on.year})
        page.goto(f'{live_server.url}{url}')
        expected_date = article.posted_on.strftime('%B %d, %Y')
        assert page.locator(f'h2:has-text("{expected_date}")').is_visible()

    def test_shows_article_content(self, page, live_server, article):
        url = reverse('news:by_year', kwargs={'year': article.posted_on.year})
        page.goto(f'{live_server.url}{url}')
        assert page.locator('text=Full content').is_visible()

    def test_empty_year(self, page, live_server):
        url = reverse('news:by_year', kwargs={'year': 1999})
        page.goto(f'{live_server.url}{url}')
        articles = page.locator('#centerColumn h2')
        assert articles.count() == 0

    def test_article_anchor_id(self, page, live_server, article):
        url = reverse('news:by_year', kwargs={'year': article.posted_on.year})
        page.goto(f'{live_server.url}{url}')
        anchor = page.locator(f'#{slugify(article.title)}')
        assert anchor.is_visible()


class TestNewsCurrent:
    def test_page_loads(self, page, live_server):
        page.goto(f'{live_server.url}{reverse("news:current_news_articles")}')
        assert page.locator('body').is_visible()

    def test_shows_nothing_when_empty(self, page, live_server):
        page.goto(f'{live_server.url}{reverse("news:current_news_articles")}')
        assert page.locator('text=Nothing at the moment').is_visible()

    def test_shows_article_when_current(self, page, live_server, current_article):
        page.goto(f'{live_server.url}{reverse("news:current_news_articles")}')
        assert page.locator(f'text={current_article.title}').is_visible()

    def test_hides_expired_article(self, page, live_server, article):
        page.goto(f'{live_server.url}{reverse("news:current_news_articles")}')
        assert page.locator('text=Nothing at the moment').is_visible()
