# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-05-05 16:54
from __future__ import unicode_literals

from django.db import migrations


# noinspection PyUnusedLocal
def backwards_func(apps, schema_editor):
    apps.get_model('auth', 'Group').objects.get(name='Bow Hunt').delete()


# noinspection PyUnusedLocal
def forwards_func(apps, schema_editor):
    group_model = apps.get_model('auth', 'Group')
    group_model.objects.create(name='Bow Hunt')


class Migration(migrations.Migration):

    dependencies = [
        ('bow_hunt', '0010_listed_hunter_incorrect_error'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func)
    ]
