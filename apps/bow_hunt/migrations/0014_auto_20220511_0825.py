# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-05-11 12:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bow_hunt', '0013_move_deer_info'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='log',
            name='deer_count',
        ),
        migrations.RemoveField(
            model_name='log',
            name='deer_gender',
        ),
        migrations.RemoveField(
            model_name='log',
            name='deer_points',
        ),
        migrations.RemoveField(
            model_name='log',
            name='deer_tracking',
        ),
    ]