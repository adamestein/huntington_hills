from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

DEFAULT_ONCLICK = "return showAddAnotherPopup(this);"
DEFAULT_URL = '/admin/bow_hunt/%(field)s/add/?_to_field=id&_popup=1'


class MultipleSelectWithAdd(forms.SelectMultiple):
    def __init__(self, attrs=None, choices=()):
        defaults = _set_popup_defaults(attrs)
        super(MultipleSelectWithAdd, self).__init__(attrs, choices)
        self.popup_add = _create_popup_anchor(defaults)

    def render(self, name, value, attrs=None, renderer=None):
        html = super(MultipleSelectWithAdd, self).render(name, value, attrs, renderer)
        return mark_safe(
            html + self.popup_add % {
                'field': name.replace('_', ''),
                'id_name': name,
                'name': name.replace('_', ' '),
                'static_url': settings.STATIC_URL
            }
        )


class SelectWithAdd(forms.Select):
    def __init__(self, attrs=None, choices=()):
        defaults = _set_popup_defaults(attrs)
        super(SelectWithAdd, self).__init__(attrs, choices)
        self.popup_add = _create_popup_anchor(defaults)

    def render(self, name, value, attrs=None, renderer=None):
        html = super(SelectWithAdd, self).render(name, value, attrs, renderer)
        return mark_safe(
            html + self.popup_add % {
                'field': name.replace('_', ''),
                'id_name': name,
                'name': name.replace('_', ' '),
                'static_url': settings.STATIC_URL
            }
        )


def _create_popup_anchor(values):
    anchor = f"""
        <a href="{values['url']}" class="add-another" id="add_id_%(id_name)s" onclick="{values['onclick']}" 
           title="Add another %(name)s">
            <img src="%(static_url)simg/icon-addlink.svg" alt="Add">
        </a>
    """

    return anchor


def _set_popup_defaults(attrs):
    if attrs:
        defaults = {
            'onclick': attrs.pop('onclick', DEFAULT_ONCLICK),
            'url': attrs.pop('url', DEFAULT_URL)
        }
    else:
        defaults = {
            'onclick': DEFAULT_ONCLICK,
            'url': DEFAULT_URL
        }

    return defaults
