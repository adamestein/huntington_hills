# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-07-17 17:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bow_hunt', '0024_set_up_sites'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='site',
            options={'ordering': ('number', 'street')},
        ),
    ]