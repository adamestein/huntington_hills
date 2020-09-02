from django.contrib import admin

from .models import Owner, Photo

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_filter = ('owner',)

    search_fields = ('owner__name', 'short_description')


admin.site.register(Owner)
