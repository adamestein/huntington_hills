# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2025-03-08 18:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mailing_lists', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mailinglist',
            name='email_type',
        ),
    ]
