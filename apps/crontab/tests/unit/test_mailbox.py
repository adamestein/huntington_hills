import pytest
from django.core.management import get_commands

from django_mailbox.models import Mailbox

from crontab.mailbox import process_mailboxes


class FakeMessage:
    """Stands in for the django_mailbox Message in the tests."""

    def __init__(self, subject):
        self.subject = subject
        self.from_address = 'test@example.com'


class FakeTransport:
    """Stands in for the django_mailbox transports in the tests."""

    def __init__(self, messages):
        self.messages = messages
        self.closed = False

    def get_message(self, condition=None):
        yield from self.messages

    def close(self):
        self.closed = True


@pytest.mark.django_db
class TestProcessMailboxes:

    def test_getmail_command_is_overridden(self):
        """The crontab app's getmail command has to take precedence over django_mailbox's."""
        assert get_commands()['getmail'] == 'crontab'

    def test_a_bad_message_does_not_stop_the_other_messages(self, monkeypatch):
        """
        One message that cannot be processed must not stop the rest of the mail.

        django_mailbox's getmail command aborts the whole run in that case, which leaves
        every mailbox it has not reached yet unprocessed.
        """
        Mailbox.objects.create(name='Residents')

        processed = []

        def fake_process_incoming_message(mailbox, message):
            if message.subject == 'bad':
                raise ValueError('Invalid address')
            processed.append(message.subject)
            return message

        monkeypatch.setattr(
            Mailbox, 'get_connection',
            lambda self: FakeTransport([FakeMessage('first'), FakeMessage('bad'), FakeMessage('second')])
        )
        monkeypatch.setattr(Mailbox, 'process_incoming_message', fake_process_incoming_message)

        process_mailboxes()

        assert processed == ['first', 'second']

    def test_only_the_named_mailboxes_are_processed(self, monkeypatch):
        Mailbox.objects.create(name='Residents')
        Mailbox.objects.create(name='Board')

        processed = []

        def fake_process_incoming_message(mailbox, message):
            processed.append((mailbox.name, message.subject))
            return message

        monkeypatch.setattr(Mailbox, 'get_connection', lambda self: FakeTransport([FakeMessage('message')]))
        monkeypatch.setattr(Mailbox, 'process_incoming_message', fake_process_incoming_message)

        process_mailboxes(['Board'])

        assert processed == [('Board', 'message')]
