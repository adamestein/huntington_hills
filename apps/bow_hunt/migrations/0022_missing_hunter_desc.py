# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-06-13 12:19
from __future__ import unicode_literals

from django.db import migrations


# noinspection PyUnusedLocal
def backwards_func(apps, schema_editor):
    data_warning_model = apps.get_model('bow_hunt', 'DataWarning')
    missing_hunter = data_warning_model.objects.get(label='Hunter was missing from the IPD log')
    missing_hunter.description = ''
    missing_hunter.save()


# noinspection PyUnusedLocal
def forwards_func(apps, schema_editor):
    data_warning_model = apps.get_model('bow_hunt', 'DataWarning')
    missing_hunter = data_warning_model.objects.get(label='Hunter was missing from the IPD log')
    missing_hunter.description = 'The IPD log fails to show this hunter at this location even though there is evidence to support it.'
    missing_hunter.save()


class Migration(migrations.Migration):

    dependencies = [
        ('bow_hunt', '0021_logsheet_comment'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func)
    ]