import logging

logger = logging.getLogger(__name__)

from django_mailbox.models import Mailbox


def process_mailboxes():
    for mailbox in Mailbox.objects.filter(name='Spring Valley'):
        logger.info(f'Gathering messages for {mailbox.name}')
        messages = mailbox.get_new_mail()
        for message in messages:
            logger.info(f'Received {message.subject} (from {message.from_address})')
        else:
            logger.info(f'No new mail for {mailbox.name}')
