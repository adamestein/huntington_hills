from datetime import date

import pytest

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


@pytest.mark.django_db
class TestArticleStr:
    def test_str(self, article):
        result = str(article)
        assert '[2024-06-15] Test Article' in result


@pytest.mark.django_db
class TestArticleDefaultPostedOn:
    def test_posted_on_defaults_to_today(self, db):
        article = Article.objects.create(
            title='Fresh Article',
            short_desc='Brand new',
            desc='<p>Just posted</p>',
            posted_until=date(2024, 8, 1),
        )
        assert article.posted_on == date.today()

    def test_posted_on_respected_when_set(self, article):
        assert article.posted_on == date(2024, 6, 15)


@pytest.mark.django_db
class TestArticleMetaOrdering:
    def test_ordering(self):
        assert Article._meta.ordering == ('-posted_on', 'title')


@pytest.mark.django_db
class TestArticleTitleUnique:
    def test_unique_title(self):
        Article.objects.create(
            title='Unique Title',
            short_desc='First',
            desc='<p>First</p>',
            posted_on=date.today(),
            posted_until=date.today(),
        )
        with pytest.raises(Exception):
            Article.objects.create(
                title='Unique Title',
                short_desc='Duplicate',
                desc='<p>Duplicate</p>',
                posted_on=date.today(),
                posted_until=date.today(),
            )


@pytest.mark.django_db
class TestArticleFields:
    def test_short_desc_max_length(self):
        field = Article._meta.get_field('short_desc')
        assert field.max_length == 200

    def test_title_max_length(self):
        field = Article._meta.get_field('title')
        assert field.max_length == 50
