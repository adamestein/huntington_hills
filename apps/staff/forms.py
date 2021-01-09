from datetime import date

from django import forms

from library.forms import RequiredFormSet

from residents.models import Board, Person


class UpdateBoardMembersForm(forms.ModelForm):
    elected_date = forms.DateField(initial=date.today)

    class Meta:
        # We list all the fields so that we can specify the order in which they appear on the page
        fields = ['president', 'vice_president', 'treasurer', 'secretary', 'director_at_large_1', 'director_at_large_2']
        model = Board


class UpdateHomeownersForm(forms.ModelForm):
    class Meta:
        fields = ('prefix', 'first_name', 'last_name', 'suffix', 'phone')
        model = Person


UpdateHomeownersFormSet = forms.models.modelformset_factory(
    Person, extra=2, form=UpdateHomeownersForm, formset=RequiredFormSet
)
