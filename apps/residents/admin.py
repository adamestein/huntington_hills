from django.contrib import admin

from .models import Email, EmailType, LotNumber, MailingAddress, Person, Property, PropertyType, Street


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_filter = ('email_type',)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_filter = ('residential_property__street',)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_filter = ('street',)


admin.site.register(EmailType)
admin.site.register(LotNumber)
admin.site.register(MailingAddress)
admin.site.register(PropertyType)
admin.site.register(Street)
