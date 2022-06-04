from django import forms
from django.contrib import admin
from django.core.exceptions import FieldError, ObjectDoesNotExist, ValidationError
from django.db.models.functions import ExtractYear

from .models import DataWarning, Deer, Hunter, Location, Log, LogSheet, NonHunter, Officer


class DataWarningAdmin(admin.ModelAdmin):
    list_filter = ('type',)


class DeerAdminForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Deer

    def clean(self):
        cleaned_data = super().clean()
        count = cleaned_data['count']
        gender = cleaned_data['gender']
        log = cleaned_data.get('log')
        points = cleaned_data['points']
        tracking = cleaned_data['tracking']

        if count:
            if log is None or (log.hunter is None and not hasattr(log, 'nonhunter')):
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
    search_fields = ('log__hunter__first_name', 'log__hunter__last_name')


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
    search_fields = ('first_name', 'last_name')


class LocationAdmin(admin.ModelAdmin):
    list_filter = ('year',)
    search_fields = ('address',)


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


class _LogSheetYearFilter(admin.SimpleListFilter):
    title = 'year'
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        return [
            (year, year) for year in
            LogSheet.objects.dates('date', 'year')
            .annotate(year=ExtractYear('date'))
            .order_by('year')
            .values_list('year', flat=True)
        ]

    def queryset(self, request, queryset):
        if self.value() is not None:
            try:
                return queryset.filter(log_sheet__date__year=self.value())
            except FieldError:
                return queryset.filter(date__year=self.value())
        return queryset


class LogAdmin(admin.ModelAdmin):
    form = LogAdminForm
    list_filter = (_LogSheetYearFilter,)
    search_fields = ('hunter__first_name', 'hunter__last_name')


class LogSheetAdmin(admin.ModelAdmin):
    list_filter = (_LogSheetYearFilter,)


admin.site.register(DataWarning, DataWarningAdmin)
admin.site.register(Deer, DeerAdmin)
admin.site.register(Hunter, HunterAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(LogSheet, LogSheetAdmin)
admin.site.register(NonHunter)
admin.site.register(Officer)
