# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2025-03-22 23:34
from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations
from django.utils.text import slugify

import upsilonconf

from residents.models import Board

DOMAIN = 'huntingtonhillsinc.website'
EMAIL = 'board'
ML_NAME = 'Board'


# noinspection PyUnusedLocal
def backwards_func(apps, schema_editor):
    mailbox = apps.get_model('django_mailbox', 'Mailbox').objects.get(name=ML_NAME)
    apps.get_model('mailing_lists', 'MailingList').objects.get(mailbox=mailbox).delete()
    mailbox.delete()


# noinspection PyUnusedLocal
def forwards_func(apps, schema_editor):
    django_mailbox_model = apps.get_model('django_mailbox', 'Mailbox')
    email_model = apps.get_model('residents', 'Email')
    mailing_list_model = apps.get_model('mailing_lists', 'MailingList')
    person_model = apps.get_model('residents', 'Person')

    bounce_email = f'{EMAIL}-bounces@{DOMAIN}'
    config = upsilonconf.load('.env.json')['Mailing Lists']
    email = f'{EMAIL}@{DOMAIN}'

    mailbox = django_mailbox_model.objects.create(
        name=ML_NAME,
        uri=f'pop3+ssl://{email}:{config["credentials"][ML_NAME].password}@{config.host}:995'
    )

    ml = mailing_list_model.objects.create(
        email=email,
        mailbox=mailbox,
        name_slug=slugify(ML_NAME)
    )

    for member_email in Board.objects.first().get_email_list():
        try:
            email_obj = email_model.objects.get(email=member_email)
        except ObjectDoesNotExist:
            # Can't find email in system, so don't add the person
            pass
        else:
            ml.members.add(email_obj)

    print(f'''

Remember to create 2 emails (if not already done so):

    1) {email}, which is just a regular mailbox AND
    2) {bounce_email}, which is forwarded to the postmaster
''')


class Migration(migrations.Migration):

    dependencies = [
        ('mailing_lists', '0011_fill_in_name_slug'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func)
    ]
