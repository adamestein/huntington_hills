# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-04-17 18:13
from __future__ import unicode_literals

from django.db import migrations

from bow_hunt.models import DataWarning


# noinspection PyUnusedLocal
def backwards_func(apps, schema_editor):
    apps.get_model('bow_hunt', 'DataWarning').objects.get(label='Hunter first name missing').delete()


# noinspection PyUnusedLocal
def forwards_func(apps, schema_editor):
    data_warning_model = apps.get_model('bow_hunt', 'DataWarning')

    data_warning_model.objects.create(
        description=(
            'Only a last name for a hunter was given and there are several hunters in the program with the same '
            'last name. No way to tell which hunter it was.'
        ),
        label='Hunter first name missing',
        type=DataWarning.MISSING_WARNING
    )


class Migration(migrations.Migration):

    dependencies = [
        ('bow_hunt', '0008_auto_20220414_0848'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func)
    ]