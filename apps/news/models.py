from datetime import date

from django.db import models


class Article(models.Model):
    desc = models.TextField()
    posted_on = models.DateField(blank=True)
    posted_until = models.DateField(help_text='Last date in which to display this article')
    short_desc = models.CharField(max_length=200)
    title = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ('-posted_on', 'title')

    def save(self, **kwargs):
        if self.posted_on is None:
            self.posted_on = date.today()

        super().save(**kwargs)

    def __str__(self):
        return f'[{self.posted_on}] {self.title}'
