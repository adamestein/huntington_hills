import logging

logger = logging.getLogger(__name__)

from django_mailbox.models import Mailbox
from django.utils.timezone import now


def process_mailboxes(mailbox_names=None):
    # Uncomment to show all log messages in PyCharm console window when running this cronjob
    # logging.basicConfig(level=logging.DEBUG)

    mailboxes = Mailbox.active_mailboxes.all()
    if mailbox_names:
        mailboxes = mailboxes.filter(name__in=mailbox_names)

    for mailbox in mailboxes:
        logger.info(f'Gathering messages for {mailbox.name}')

        connection = mailbox.get_connection()
        if not connection:
            continue

        num_msgs = 0

        try:
            for message in connection.get_message():
                try:
                    processed = mailbox.process_incoming_message(message)
                    if processed is not None:
                        num_msgs += 1
                        logger.info(f'Received {processed.subject} (from {processed.from_address})')
                except Exception as e:
                    # A single bad message must not stop the rest of the mail from being
                    # processed, so log it and keep going. The message itself is still
                    # saved in the django_mailbox Message table.
                    logger.error(f'{mailbox.name}: {e}', exc_info=True)
                    continue
        except Exception as e:
            logger.error(f'{mailbox.name}: {e}', exc_info=True)
        finally:
            connection.close()

        mailbox.last_polling = now()
        mailbox.save(update_fields=['last_polling'])

        if num_msgs == 0:
            logger.info(f'No new mail for {mailbox.name}')
