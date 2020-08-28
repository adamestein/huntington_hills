from django.contrib import admin

from .models import Board, Email, EmailType, LotNumber, MailingAddress, Person, Property, PropertyType, Street


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = (
        'president_full_name' , 'vice_president_full_name', 'treasurer_full_name', 'secretary_full_name',
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


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_filter = ('email_type',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'person':
            kwargs['queryset'] = Person.objects.filter(active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_filter = ('residential_property__street',)

    search_fields = ('first_name', 'last_name')


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_filter = ('street',)


admin.site.register(EmailType)
admin.site.register(LotNumber)
admin.site.register(MailingAddress)
admin.site.register(PropertyType)
admin.site.register(Street)
