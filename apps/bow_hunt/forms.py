import logging

from django import forms
from django.core.exceptions import ValidationError
from django.db.models.functions import ExtractYear
from django.utils import six
from django.utils.encoding import force_text
from django.utils.html import conditional_escape

from .models import Deer, Hunter, Location, Log, LogSheet

from library.forms import MultipleSelectWithAdd, SelectWithAdd

logger = logging.getLogger(__name__)

DEER_PREFIX = 'deer'
HUNTER_PREFIX = 'hunter'


class DeerForm(forms.ModelForm):
    hunter_formset_number = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        # Sets the order the fields will be displayed
        fields = ['count', 'gender', 'points', 'tracking', 'log', 'hunter_formset_number']
        model = Deer
        widgets = {'log': forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        log_required = kwargs.pop('log_required', False)
        super().__init__(*args, **kwargs)
        if not log_required:
            self.fields['log'].required = False

    def clean(self):
        cleaned_data = super().clean()
        count = cleaned_data['count']
        gender = cleaned_data['gender']
        points = cleaned_data['points']
        tracking = cleaned_data['tracking']

        if count:
            log = cleaned_data['log']

            if log.hunter is None:
                raise forms.ValidationError(
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
            if gender is not None:
                self.add_error('gender', 'Gender is set but the count equals 0')

            if points is not None:
                if gender == Deer.GENDER_MALE:
                    self.add_error('points', 'Points is set but the count equals 0')
                else:
                    self.add_error('points', 'Points is set but the count equals 0 and the gender is Female')

            if tracking is not None:
                self.add_error('tracking', 'Tracking is set but the count equals 0')

        return cleaned_data


DeerFormSet = forms.formset_factory(DeerForm, extra=0)


class HunterAnalysisForm(forms.Form):
    year_choices = [
        (year, year) for year in
        LogSheet.objects.dates('date', 'year')
        .annotate(year=ExtractYear('date'))
        .order_by('year')
        .values_list('year', flat=True)
    ]

    years = forms.MultipleChoiceField(choices=year_choices, label='', widget=forms.SelectMultiple(attrs={'size': 20}))

    hunter_choices = [(hunter.id, str(hunter)) for hunter in Hunter.objects.exclude(first_name='<unknown>')]

    hunters = forms.MultipleChoiceField(
        choices=hunter_choices, label='', widget=forms.SelectMultiple(attrs={'size': 20})
    )


class HunterForm(forms.ModelForm):
    hunter_formset_number = forms.IntegerField(widget=forms.HiddenInput())
    location_id = forms.IntegerField(widget=forms.HiddenInput())    # Store only the ID, so we can avoid the large list
    log_sheet_id = forms.IntegerField(widget=forms.HiddenInput())   # Store only the ID, so we can avoid the large list
    pk = forms.IntegerField(required=False, widget=forms.HiddenInput())  # Need this to add instance to form later

    class Meta:
        exclude = ['location', 'log_sheet']
        model = Log
        widgets = {
            'hunter': SelectWithAdd(),
            'incorrect_warnings': forms.CheckboxSelectMultiple,
            'missing_warnings': forms.CheckboxSelectMultiple
        }

    def as_table(self):
        return self._as_table('hunter') + \
               '<tr><th>Deer</th><td></td></tr>' + \
               self._as_table('comment')

    def _as_table(self, field_name):
        bf = self[field_name]
        bf_errors = self.error_class([conditional_escape(error) for error in bf.errors])

        if bf.label:
            label = conditional_escape(force_text(bf.label))
            label = bf.label_tag(label) or ''
        else:
            label = ''

        if self.fields[field_name].help_text:
            help_text = f'<span class="helptext">{force_text(self.fields[f"{field_name}"].help_text)}</span>'
        else:
            help_text = ''

        error_row = f'<tr><td colspan="2">{force_text(bf_errors)}</td></tr>' if bf_errors else ''

        if field_name == 'hunter':
            return f"""
                {error_row}
                <tr>
                    <th>{label}</th>
                    <td>
                        {six.text_type(self['pk'])}
                        {six.text_type(self['log_sheet_id'])}
                        {six.text_type(self['location_id'])}
                        {six.text_type(self['hunter_formset_number'])}
                        {six.text_type(bf)}{help_text}<br />
                        {six.text_type(self['missing_warnings'])}
                        {six.text_type(self['incorrect_warnings'])}
                    </td>
                </tr>
            """
        else:
            return f"""
                {error_row}
                <tr>
                    <th>{label}</th>
                    <td>{six.text_type(bf)}{help_text}</td>
                </tr>
            """


HunterFormSet = forms.formset_factory(HunterForm, extra=0)


class LocationForm(forms.Form):
    location = forms.ModelMultipleChoiceField(
        Location.objects.none(), label='', widget=MultipleSelectWithAdd(attrs={'size': 20})
    )

    def __init__(self, **kwargs):
        self.year = kwargs.pop('year')
        super().__init__()
        self.fields['location'].queryset = Location.objects.filter(year=self.year)
        self.initial['location'] = kwargs.get('initial', {'location': []})['location']

    def as_p(self):
        html = super().as_p()
        return html.replace('<p>', '<p id="location_list">').replace(f'[{self.year}] ', '')


class LogSheetForm(forms.Form):
    log_sheet = forms.ModelChoiceField(LogSheet.objects.all(), widget=SelectWithAdd())
