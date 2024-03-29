# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-05-06 23:12
from __future__ import unicode_literals

from django.db import migrations


# noinspection PyUnusedLocal
def backwards_func(apps, schema_editor):
    raise RuntimeError('If we need to go backwards, implement grouping by log so that we can put back deer qty')


# noinspection PyUnusedLocal
def forwards_func(apps, schema_editor):
    deer_model = apps.get_model('bow_hunt', 'Deer')
    log_model = apps.get_model('bow_hunt', 'Log')

    for log in log_model.objects.exclude(deer_count=0):
        deer_model.objects.create(
            count=log.deer_count,
            gender=log.deer_gender,
            log=log,
            points=log.deer_points,
            tracking=log.deer_tracking
        )


class Migration(migrations.Migration):

    dependencies = [
        ('bow_hunt', '0012_deer'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func)
    ]
