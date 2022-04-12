from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Hunter, Location, Log, LogSheet, Officer


class HunterAdminForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Hunter

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data['first_name']
        last_name = cleaned_data['last_name']

        if not first_name and not last_name:
            raise ValidationError('Need a first or last name, both can not be blank')


class LogAdminForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Log

    def clean(self):
        cleaned_data = super().clean()
        count = cleaned_data['deer_count']
        gender = cleaned_data['deer_gender']
        hunter = cleaned_data['hunter']
        location = cleaned_data['location']
        log_sheet = cleaned_data['log_sheet']
        points = cleaned_data['deer_points']
        tracking = cleaned_data['deer_tracking']

        # Can't seem to set unique_together for these fields (migration has a duplicate entry for the log sheet key
        # error), so we'll just check here
        if Log.objects.filter(location=location, log_sheet=log_sheet).exists():
            raise ValidationError(f'Log with this Location and Log sheet already exists.')

        if location.year != log_sheet.date.year:
            raise ValidationError(
                f'Mismatch between location year ({location.year}) and log sheet year ({log_sheet.date.year}'
            )

        if count:
            if hunter is None:
                raise ValidationError(
                    (
                        'Hunter needs to be specified when any deer are shot or killed. '
                        'If not specified, list first name as <unknown>.'
                    ),
                    code='invalid'
                )

            if gender is None:
                raise ValidationError('Need to specify the deer gender when any are shot or killed', code='invalid')

            if gender == Log.GENDER_MALE and points is None:
                raise ValidationError('Male deer need the number of points specified', code='invalid')

            if tracking is None:
                raise ValidationError(
                    'Need to specify if tracking was required when any deer are shot or killed', code='invalid'
                )

        return cleaned_data


class HunterAdmin(admin.ModelAdmin):
    form = HunterAdminForm


class LogAdmin(admin.ModelAdmin):
    form = LogAdminForm


admin.site.register(Log, LogAdmin)
admin.site.register(Hunter, HunterAdmin)
admin.site.register(Location)
admin.site.register(LogSheet)
admin.site.register(Officer)
