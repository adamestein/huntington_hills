# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-12-31 19:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bow_hunt', '0026_incorrect_tracking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datawarning',
            name='label',
            field=models.CharField(max_length=70),
        ),
    ]
