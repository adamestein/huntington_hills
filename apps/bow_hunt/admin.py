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
        incorrect_error = cleaned_data['incorrect_in_ipd_log']
        incorrect_warnings = cleaned_data['incorrect_warnings']
        location = cleaned_data['location']
        log_sheet = cleaned_data['log_sheet']
        missing_error = cleaned_data['missing_from_ipd_log']
        missing_warnings = cleaned_data['missing_warnings']
        points = cleaned_data['deer_points']
        tracking = cleaned_data['deer_tracking']

        # Database level restriction doesn't seem to work when Hunter = None, so we'll test for that here
        if self.instance.id is None and hunter is None and \
                Log.objects.filter(hunter=hunter, location=location, log_sheet=log_sheet).exists():
            raise ValidationError('Log with this Log sheet, Location and Hunter already exists.')

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

        if incorrect_error and incorrect_warnings.count() == 0:
            raise ValidationError('An incorrect error is specified, but no warnings were selected')

        if incorrect_warnings.count() and not incorrect_error:
            raise ValidationError('Incorrect warnings were selected, but no incorrect error was specified')

        if missing_error and missing_warnings.count() == 0:
            raise ValidationError('A missing error is specified, but no warnings were selected')

        if missing_warnings.count() and not missing_error:
            raise ValidationError('Missing warnings were selected, but no missing error was specified')

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
