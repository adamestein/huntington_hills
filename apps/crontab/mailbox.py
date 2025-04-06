import logging

logger = logging.getLogger(__name__)

from django_mailbox.models import Mailbox


def process_mailboxes():
    # Uncomment to show all log messages in PyCharm console window when running this cronjob
    # logging.basicConfig(level=logging.DEBUG)

    for mailbox in Mailbox.active_mailboxes.all():
        logger.info(f'Gathering messages for {mailbox.name}')

        messages = mailbox.get_new_mail()
        num_msgs = 0

        try:
            for message in messages:
                logger.info(f'Received {message.subject} (from {message.from_address})')
                num_msgs += 1
        except Exception as e:
            logger.error(f'{mailbox.name}: {e}')

        if num_msgs == 0:
            logger.info(f'No new mail for {mailbox.name}')

