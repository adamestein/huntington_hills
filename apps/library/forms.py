from django.forms import BaseFormSet


class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.pop('queryset')      # Just in case it's there
        unrequired = kwargs.pop('unrequired')

        super().__init__(*args, **kwargs)

        for index, form in enumerate(self.forms):
            if index not in unrequired:
                form.empty_permitted = False
