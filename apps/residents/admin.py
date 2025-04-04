from django.contrib import admin

from .models import (
    Board, BoardTerm, Email, LotNumber, MailingAddress, Person, Property, PropertyType, Street, PersonEmail
)


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = (
        'president_full_name', 'vice_president_full_name', 'treasurer_full_name', 'secretary_full_name',
        'director_at_large_1_full_name', 'director_at_large_2_full_name'
    )

    def director_at_large_1_full_name(self, obj):
        return obj.director_at_large_1.full_name
    director_at_large_1_full_name.short_description = 'Director At Large'

    def director_at_large_2_full_name(self, obj):
        return obj.director_at_large_2.full_name
    director_at_large_2_full_name.short_description = 'Director At Large'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs['queryset'] = Person.objects.filter(active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def president_full_name(self, obj):
        return obj.president.full_name
    president_full_name.short_description = 'President'

    def secretary_full_name(self, obj):
        return obj.secretary.full_name
    secretary_full_name.short_description = 'Secretary'

    def treasurer_full_name(self, obj):
        return obj.treasurer.full_name
    treasurer_full_name.short_description = 'Treasurer'

    def vice_president_full_name(self, obj):
        return obj.vice_president.full_name
    vice_president_full_name.short_description = 'Vice President'


@admin.register(BoardTerm)
class BoardTermAdmin(admin.ModelAdmin):
    list_filter = ('office',)

    search_fields = ('person__first_name', 'person__last_name')


class PersonEmailInline(admin.TabularInline):
    model = PersonEmail


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = (PersonEmailInline,)
    list_filter = ('residential_property__street',)
    search_fields = ('first_name', 'last_name')


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_filter = ('street',)


admin.site.register(PersonEmail)
admin.site.register(Email)
admin.site.register(LotNumber)
admin.site.register(MailingAddress)
admin.site.register(PropertyType)
admin.site.register(Street)
