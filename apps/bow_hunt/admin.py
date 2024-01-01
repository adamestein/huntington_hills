from django import forms
from django.contrib import admin
from django.core.exceptions import FieldError, ValidationError
from django.db.models import Q
from django.db.models.functions import ExtractYear

from .models import (
    AdjacentSite, DataWarning, Deer, Hunter, Location, Log, LogSheet, LogSheetNonIPD, NonHunter, Officer, Site
)


class _LogSheetYearFilter(admin.SimpleListFilter):
    parameter_name = 'year'
    title = 'year'

    def lookups(self, request, model_admin):
        if str(model_admin) in ['bow_hunt.LogAdmin', 'bow_hunt.DeerAdmin']:
            years = [
                (year, year) for year in
                LogSheet.objects.dates('date', 'year')
                .annotate(year=ExtractYear('date'))
                .order_by('year')
                .values_list('year', flat=True)
            ] + [
                (year, year) for year in
                LogSheetNonIPD.objects.dates('date', 'year')
                .annotate(year=ExtractYear('date'))
                .order_by('year')
                .values_list('year', flat=True)
            ]
        else:
            years = [
                (year, year) for year in
                model_admin.model.objects.dates('date', 'year')
                .annotate(year=ExtractYear('date'))
                .order_by('year')
                .values_list('year', flat=True)
            ]

        return sorted(years)

    def queryset(self, request, queryset):
        if self.value() is not None:
            if queryset.model.__name__ == 'Deer':
                query = Q(log__log_sheet__date__year=self.value()) | Q(log__log_sheet_non_ipd__date__year=self.value())
                return queryset.filter(query)
            elif queryset.model.__name__ == 'Log':
                query = Q(log_sheet__date__year=self.value()) | Q(log_sheet_non_ipd__date__year=self.value())
                return queryset.filter(query)
            elif queryset.model.__name__ in ['LogSheet', 'LogSheetNonIPD']:
                return queryset.filter(date__year=self.value())
            else:
                raise RuntimeError(f'do not know how to filter years for {queryset.model.__name__}')
        return queryset


class AdjacentSiteAdminForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = AdjacentSite

    def clean(self):
        cleaned_data = super().clean()
        count_true = sum([
            cleaned_data['is_durand_eastman_golf_course'],
            cleaned_data['is_durand_eastman_park'],
            cleaned_data['is_hh_commons'],
            cleaned_data['is_irondequoit_bay_park_west'],
            cleaned_data['is_irondequoit_town_land'],
            cleaned_data['is_vacant']
        ])

        if count_true == 0:
            raise ValidationError('One is_... flag must be specified')
        elif count_true > 1:
            raise ValidationError('Only one is_... flag can be specified')

        return cleaned_data


@admin.register(AdjacentSite)
class AdjacentSiteAdmin(admin.ModelAdmin):
    form = AdjacentSiteAdminForm
    list_filter = ('is_hh_commons', 'is_vacant')


@admin.register(DataWarning)
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


@admin.register(Deer)
class DeerAdmin(admin.ModelAdmin):
    form = DeerAdminForm
    list_filter = (_LogSheetYearFilter,)
    raw_id_fields = ('log',)
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


@admin.register(Hunter)
class HunterAdmin(admin.ModelAdmin):
    form = HunterAdminForm
    search_fields = ('first_name', 'last_name')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_filter = ('year',)
    search_fields = ('label',)


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


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    form = LogAdminForm
    list_filter = (_LogSheetYearFilter,)
    search_fields = ('hunter__first_name', 'hunter__last_name')


@admin.register(LogSheet)
class LogSheetAdmin(admin.ModelAdmin):
    list_filter = (_LogSheetYearFilter,)


@admin.register(LogSheetNonIPD)
class LogSheetNonIPDAdmin(admin.ModelAdmin):
    list_filter = (_LogSheetYearFilter,)


@admin.register(NonHunter)
class NonHunterAdmin(admin.ModelAdmin):
    raw_id_fields = ('log',)


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_filter = ('town_owned',)
    search_fields = ('number', 'secondary_number', 'street',)
