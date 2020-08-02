from django.template.defaulttags import register


@register.filter
def dict_lookup(dictionary, key):
    return dictionary.get(key) if dictionary is not None and key is not None else None
