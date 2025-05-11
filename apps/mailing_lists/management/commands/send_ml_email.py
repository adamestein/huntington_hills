import sys

from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage, get_connection

import upsilonconf


class Command(BaseCommand):
    help = 'Send an email using the mailing list SMTP values'

    def add_arguments(self, parser):
        parser.add_argument(
            'from_email', default='spring_valley@huntingtonhillsinc.org', nargs='?', type=str, help='From email'
        )

        parser.add_argument('--subject', default='Test Email', nargs='?', type=str, help='Subject of the email')

        parser.add_argument(
            '--to', action='append', required=True, type=str,
            help='Email address to send to (can be specified multiple times)'
        )

    def handle(self, *args, **kwargs):
        config = upsilonconf.load('.env.json')['Mailing Lists']

        connection_args = {
            'host': config.host,
            'password': config.password,
            'port': config.port,
            'use_tls': True,
            'username': config.username
        }

        with get_connection(**connection_args) as connection:
            msg = EmailMessage(
                body='Test Message',
                connection=connection,
                from_email=kwargs['from_email'],
                headers={
                    'From': kwargs['from_email']
                },
                subject=kwargs['subject'],
                to=kwargs['to']
            )

            try:
                msg.send()
            except Exception as e:
                print(f'Error sending test email: {e}', file=sys.stderr)
