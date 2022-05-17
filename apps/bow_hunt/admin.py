from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import DataWarning, Deer, Hunter, Location, Log, LogSheet, Officer


class DeerAdminForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Deer

    def clean(self):
        cleaned_data = super().clean()
        count = cleaned_data['count']
        gender = cleaned_data['gender']
        points = cleaned_data['points']
        tracking = cleaned_data['tracking']

        if count:
            if 'log' not in cleaned_data or cleaned_data['log'].hunter is None:
                self.add_error(
                    'log',
                    'Hunter needs to be specified when any deer are shot or killed. If not specified, '
                    'list first name as <unknown>.'
                )

            if gender is None:
                self.add_error('gender', 'Need to specify the deer gender when any are shot or killed')

            if gender == Deer.GENDER_MALE and points is None:
                self.add_error('points', 'Male deer need the number of points specified')

            if tracking is None:
                self.add_error(
                    'tracking', 'Need to specify if tracking was required when any deer are shot or killed'
                )
        else:
            self.add_error('count', 'No reason to save a record if no deer have been shot')

        return cleaned_data


class DeerAdmin(admin.ModelAdmin):
    form = DeerAdminForm


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


class HunterAdmin(admin.ModelAdmin):
    form = HunterAdminForm


class LogAdminForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Log

    def clean(self):
        cleaned_data = super().clean()
        hunter = cleaned_data['hunter']
        location = cleaned_data.get('location')
        log_sheet = cleaned_data.get('log_sheet')

        # Database level restriction doesn't seem to work when Hunter = None, so we'll test for that here
        if self.instance.id is None and hunter is None and \
                Log.objects.filter(hunter=hunter, location=location, log_sheet=log_sheet).exists():
            raise ValidationError('Log with this Log Sheet, Location and Hunter already exists.')

        if log_sheet and location and location.year != log_sheet.date.year:
            self.add_error(
                'location',
                f'Mismatch between location year ({location.year}) and log sheet year ({log_sheet.date.year})'
            )

        return cleaned_data


class LogAdmin(admin.ModelAdmin):
    form = LogAdminForm


admin.site.register(DataWarning)
admin.site.register(Deer, DeerAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(Hunter, HunterAdmin)
admin.site.register(Location)
admin.site.register(LogSheet)
admin.site.register(Officer)
