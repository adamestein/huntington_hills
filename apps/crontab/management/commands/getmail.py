from django.core.management.base import BaseCommand

from crontab.mailbox import process_mailboxes


class Command(BaseCommand):
    """
    Gather the new mail for the active mailboxes.

    This overrides the getmail command that django_mailbox provides. The django_mailbox
    command aborts the whole run when a single message cannot be processed, which leaves
    the mailboxes it has not reached yet unprocessed. This command isolates the errors so
    that one bad message cannot stop the rest of the mail from being processed.
    """

    help = 'Gather the new mail for the active mailboxes'

    def add_arguments(self, parser):
        parser.add_argument(
            'mailboxes', nargs='*', help='Only process the mailboxes with these names'
        )

    def handle(self, *args, **options):
        process_mailboxes(options['mailboxes'])
