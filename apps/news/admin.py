from datetime import date

from django.contrib import admin

from .models import Article


admin.site.register(Article)
