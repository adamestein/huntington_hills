# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-04-12 17:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bow_hunt', '0002_auto_20220412_0902'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='comment',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]