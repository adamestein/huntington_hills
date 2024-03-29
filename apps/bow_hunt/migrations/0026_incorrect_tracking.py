# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-12-31 17:12
from __future__ import unicode_literals

from django.db import migrations

from bow_hunt.models import DataWarning


# noinspection PyUnusedLocal
def backwards_func(apps, schema_editor):
    apps.get_model('bow_hunt', 'DataWarning').objects.filter(label='Incorrect tracking').delete()


# noinspection PyUnusedLocal
def forwards_func(apps, schema_editor):
    data_warning_model = apps.get_model('bow_hunt', 'DataWarning')

    data_warning_model.objects.create(
        description=(
            'Either the IPD sent an officer to track when it was specified there was no tracking or '
            'tracking did not occur when it was specified it was.'
        ),
        label='Incorrect tracking',
        type=DataWarning.INCORRECT_WARNING
    )


class Migration(migrations.Migration):

    dependencies = [
        ('bow_hunt', '0025_auto_20220717_1305'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func)
    ]
