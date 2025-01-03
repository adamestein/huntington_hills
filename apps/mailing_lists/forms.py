from django.forms import ModelForm

from residents.models import Person

from .models import MailingList


class MailingListAdminForm(ModelForm):
    class Meta:
        fields = '__all__'
        model = MailingList

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        possible_members = Person.objects.filter(active=True).exclude(email__isnull=True)
        self.fields['can_post'].queryset = possible_members
        self.fields['members'].queryset = possible_members
