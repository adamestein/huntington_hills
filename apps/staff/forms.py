from django import forms

from library.forms import RequiredFormSet

from residents.models import Person


class UpdateHomeownersForm(forms.ModelForm):
    class Meta:
        fields = ('prefix', 'first_name', 'last_name', 'suffix', 'phone')
        model = Person


UpdateHomeownersFormSet = forms.models.modelformset_factory(
    Person, extra=2, form=UpdateHomeownersForm, formset=RequiredFormSet
)
