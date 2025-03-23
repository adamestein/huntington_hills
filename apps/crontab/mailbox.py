import logging

logger = logging.getLogger(__name__)


def process_mailboxes():
    logger.info('Info Message')
    logger.error('Error Message')
    import sys
    print('Msg to sys.stderr', file=sys.stderr)
