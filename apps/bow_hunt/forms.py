from django import forms
from django.core.exceptions import ValidationError
from django.utils import six
from django.utils.encoding import force_text
from django.utils.html import conditional_escape

from .models import DataWarning, Location, Log, LogSheet

from library.forms import MultipleSelectWithAdd, SelectWithAdd


class HunterForm(forms.ModelForm):
    location_id = forms.IntegerField(widget=forms.HiddenInput())    # Store only the ID, so we can avoid the large list
    log_sheet_id = forms.IntegerField(widget=forms.HiddenInput())   # Store only the ID, so we can avoid the large list
    pk = forms.IntegerField(required=False, widget=forms.HiddenInput())  # Need this to add instance to form later

    class Meta:
        exclude = ['location', 'log_sheet']
        model = Log
        widgets = {
            'hunter': SelectWithAdd(),
            'missing_warnings': forms.CheckboxSelectMultiple
        }

    def as_table(self):
        return self._as_table('hunter') + \
               self._as_table('deer_count') + \
               self._as_table('deer_gender') + \
               self._as_table('deer_points') + \
               self._as_table('deer_tracking') + \
               self._as_table('comment')

    def clean(self):
        # LogAdminForm.clean(), have them point to the same code doing the checking
        cleaned_data = super().clean()
        count = cleaned_data['deer_count']
        gender = cleaned_data['deer_gender']
        hunter = cleaned_data['hunter']
        location_id = cleaned_data['location_id']
        log_sheet_id = cleaned_data['log_sheet_id']
        pk = cleaned_data.get('pk')
        points = cleaned_data['deer_points']
        tracking = cleaned_data['deer_tracking']

        log_sheet = LogSheet.objects.get(id=log_sheet_id)
        location = Location.objects.get(id=location_id)
        if pk is not None:
            self.instance = Log.objects.get(pk=pk)

        # Database level restriction doesn't seem to work when Hunter = None, so we'll test for that here
        if self.instance.id is None and hunter is None and \
                Log.objects.filter(hunter=hunter, location=location, log_sheet=log_sheet).exists():
            raise ValidationError('Log with this Log Sheet, Location and Hunter already exists.')

        if location.year != log_sheet.date.year:
            self.add_error(
                'location',
                f'Mismatch between location year ({location.year}) and log sheet year ({log_sheet.date.year})'
            )

        if count:
            if hunter is None:
                self.add_error(
                    'hunter',
                    'Hunter needs to be specified when any deer are shot or killed. If not specified, '
                    'list first name as <unknown>.'
                )

            if gender is None:
                self.add_error('deer_gender', 'Need to specify the deer gender when any are shot or killed')

            if gender == Log.GENDER_MALE and points is None:
                self.add_error('deer_points', 'Male deer need the number of points specified')

            if tracking is None:
                self.add_error(
                    'deer_tracking', 'Need to specify if tracking was required when any deer are shot or killed'
                )

        return cleaned_data

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
            missing_warnings = self['missing_warnings']

            return f"""
                {error_row}
                <tr>
                    <th>{label}</th>
                    <td>
                        {six.text_type(self['pk'])}
                        {six.text_type(self['log_sheet_id'])}
                        {six.text_type(self['location_id'])}
                        {six.text_type(bf)}{help_text}<br />
                        <span style="font-size: 90%; font-style: italic;">
                            (names can be added, but the menu is not automaticall updated)
                        </span>
                        <br />
                        {six.text_type(missing_warnings)}
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
