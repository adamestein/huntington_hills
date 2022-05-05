from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='in_group')
def in_group(user, group_name):
    try:
        return True if Group.objects.get(name=group_name) in user.groups.all() else False
    except Group.DoesNotExist:
        return False

