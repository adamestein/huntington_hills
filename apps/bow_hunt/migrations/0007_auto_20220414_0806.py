# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-04-14 12:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bow_hunt', '0006_data_warnings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='log',
            name='incorrect_in_ipd_log',
        ),
        migrations.RemoveField(
            model_name='log',
            name='missing_from_ipd_log',
        ),
    ]