import email
from io import StringIO
import json
import logging
from string import Template

import pytest
from django.conf import settings
from django.core import mail
from django.core.management import call_command

from django_mailbox.models import Mailbox, Message

from residents.models import Email

from mailing_lists.models import MailingList


FIXTURE_PATHS = [
    'apps/mailing_lists/tests/fixtures/streets.json',
    'apps/mailing_lists/tests/fixtures/property_types.json',
    'apps/mailing_lists/tests/fixtures/properties.json',
    'apps/mailing_lists/tests/fixtures/people.json',
    'apps/mailing_lists/tests/fixtures/emails.json',
    'apps/mailing_lists/tests/fixtures/people_emails.json',
]

EXPECTED_REJECTION = Template('''\
Dear $from_header,

Your message to the Residents list has been automatically rejected.

You are not authorized to post to this mailing list because your email
address is not subscribed. This list only accepts posts from subscribed
members.

If you believe this is incorrect, or you would like to request permission
to post, please contact the list administrator at:

residents_test-owner@huntingtonhillsinc.org

-----------------------------------------------------------------------

Reason for rejection:

Post by non-member to a members-only list.

---------------------------------------------------------------

Original message information:

Subject: $subject

Generic email text.
''')


@pytest.fixture
def load_fixtures():
    call_command('loaddata', *FIXTURE_PATHS)


@pytest.fixture
def mailbox():
    return Mailbox.objects.create(name='Residents')


@pytest.fixture
def resident_ml(mailbox, email1, email2):
    ml = MailingList.objects.create(
        email='residents_test@huntingtonhillsinc.org',
        mailbox=mailbox
    )
    ml.members.add(email1, email2)
    return ml


@pytest.fixture
def email1(load_fixtures):
    return Email.objects.get(email='adam@csh.rit.edu')


@pytest.fixture
def email2(load_fixtures):
    return Email.objects.get(email='randy@member.org')


@pytest.fixture
def log_stream():
    logging.disable(logging.NOTSET)
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    log = logging.getLogger('mailing_lists')
    log.setLevel(logging.INFO)
    for h in log.handlers:
        log.removeHandler(h)
    log.addHandler(handler)
    yield stream, handler
    logging.disable(logging.CRITICAL)


@pytest.mark.django_db
class TestPosting:

    def test_no_can_post_list(self, mailbox, resident_ml, email1, email2, log_stream):
        stream, handler = log_stream

        assert Message.objects.count() == 0

        message = email.message_from_bytes(b'''\
Date: Sun, 20 Jan 2013 11:53:53 -0800
Message-ID: <CAMdmm+hGH8Dgn-_0xnXJCd=PhyNAiouOYm5zFP0z-foqTO60zA@mail.gmail.com>
Subject: Member posting when no can_post list
From: Adam Stein <adam@csh.rit.edu>
To: Residents <residents_test@huntingtonhillsinc.org>
Content-Type: text/plain; charset="iso-8859-1"
Content-Transfer-Encoding: 7bit

Generic email text.
''')

        mailbox.process_incoming_message(message)
        handler.flush()

        assert len(mail.outbox) == 1
        assert mail.outbox[0].bcc == ['adam@csh.rit.edu', 'randy@member.org']
        assert mail.outbox[0].body == 'Generic email text.'
        assert mail.outbox[0].from_email == 'Adam Stein via Residents <residents_test@huntingtonhillsinc.org>'
        assert mail.outbox[0].reply_to == ['Adam Stein <adam@csh.rit.edu>']
        assert mail.outbox[0].subject == '[Residents] Member posting when no can_post list'
        assert mail.outbox[0].to == ['Residents <residents_test@huntingtonhillsinc.org>']

        headers = mail.outbox[0].extra_headers
        assert len(headers) == 11
        assert headers['From'] == 'Adam Stein via Residents <residents_test@huntingtonhillsinc.org>'
        assert headers['List-Archive'] == '<http://smeg:8002/mailing_lists/archives/list/>'
        assert headers['List-Help'] == (
            f'<http://smeg:8002/mailing_lists/lists/>,'
            f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=help%20Residents>'
        )
        assert headers['List-Owner'] == f'<mailto:{settings.DEFAULT_FROM_EMAIL}> (Contact Person for Help)'
        assert headers['List-Post'] == '<mailto:residents_test@huntingtonhillsinc.org>'
        assert headers['List-Subscribe'] == (
            f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=subscribe%20Residents>'
        )
        assert headers['List-Unsubscribe'] == (
            f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=unsubscribe%20Residents>'
        )
        assert headers['Message-ID'] == message._headers[1][1]
        assert headers['Sender'] == 'Residents <residents_test-bounces@huntingtonhillsinc.org>'
        assert headers['X-Hh-Beenthere'] == 'residents_test@huntingtonhillsinc.org'
        assert headers['X-Sender'] == 'Residents <residents_test-bounces@huntingtonhillsinc.org>'

        assert len(mail.outbox[0].alternatives) == 0

        assert stream.getvalue() == ''

        msgs = Message.objects.all()
        assert msgs.count() == 1
        assert msgs[0].subject == '[Residents] Member posting when no can_post list'

    def test_can_post_list_1(self, mailbox, resident_ml, email1, email2, log_stream):
        stream, handler = log_stream
        resident_ml.can_post.add(email1)

        assert Message.objects.count() == 0

        message = email.message_from_bytes(b'''\
Date: Sun, 20 Jan 2013 11:53:53 -0800
Message-ID: <CAMdmm+hGH8Dgn-_0xnXJCd=PhyNAiouOYm5zFP0z-foqTO60zA@mail.gmail.com>
Subject: Member posting when there is a can_post list and member is ON it
From: Adam Stein <adam@csh.rit.edu>
To: Residents <residents_test@huntingtonhillsinc.org>
Content-Type: text/plain; charset="iso-8859-1"
Content-Transfer-Encoding: 7bit

Generic email text.
''')

        mailbox.process_incoming_message(message)
        handler.flush()

        assert len(mail.outbox) == 1
        assert mail.outbox[0].bcc == ['adam@csh.rit.edu', 'randy@member.org']
        assert mail.outbox[0].body == 'Generic email text.'
        assert mail.outbox[0].from_email == 'Adam Stein via Residents <residents_test@huntingtonhillsinc.org>'
        assert mail.outbox[0].reply_to == ['Adam Stein <adam@csh.rit.edu>']
        assert mail.outbox[0].subject == (
            '[Residents] Member posting when there is a can_post list and member is ON it'
        )
        assert mail.outbox[0].to == ['Residents <residents_test@huntingtonhillsinc.org>']

        headers = mail.outbox[0].extra_headers
        assert len(headers) == 11
        assert headers['From'] == 'Adam Stein via Residents <residents_test@huntingtonhillsinc.org>'
        assert headers['List-Archive'] == '<http://smeg:8002/mailing_lists/archives/list/>'
        assert headers['List-Help'] == (
            f'<http://smeg:8002/mailing_lists/lists/>,'
            f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=help%20Residents>'
        )
        assert headers['List-Owner'] == f'<mailto:{settings.DEFAULT_FROM_EMAIL}> (Contact Person for Help)'
        assert headers['List-Post'] == '<mailto:residents_test@huntingtonhillsinc.org>'
        assert headers['List-Subscribe'] == (
            f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=subscribe%20Residents>'
        )
        assert headers['List-Unsubscribe'] == (
            f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=unsubscribe%20Residents>'
        )
        assert headers['Message-ID'] == message._headers[1][1]
        assert headers['Sender'] == 'Residents <residents_test-bounces@huntingtonhillsinc.org>'
        assert headers['X-Hh-Beenthere'] == 'residents_test@huntingtonhillsinc.org'
        assert headers['X-Sender'] == 'Residents <residents_test-bounces@huntingtonhillsinc.org>'

        assert len(mail.outbox[0].alternatives) == 0

        assert stream.getvalue() == ''

        msgs = Message.objects.all()
        assert msgs.count() == 1
        assert msgs[0].subject == (
            '[Residents] Member posting when there is a can_post list and member is ON it'
        )

    def test_can_post_list_2(self, mailbox, resident_ml, email1, email2, log_stream):
        stream, handler = log_stream
        resident_ml.can_post.add(email2)

        assert Message.objects.count() == 0

        message = email.message_from_bytes(b'''\
Date: Sun, 20 Jan 2013 11:53:53 -0800
Message-ID: <CAMdmm+hGH8Dgn-_0xnXJCd=PhyNAiouOYm5zFP0z-foqTO60zA@mail.gmail.com>
Subject: Member posting when there is a can_post list and member is NOT on it
From: Adam Stein <adam@csh.rit.edu>
To: Residents <residents_test@huntingtonhillsinc.org>
Content-Type: text/plain; charset="iso-8859-1"
Content-Transfer-Encoding: 7bit

Generic email text.
    ''')

        mailbox.process_incoming_message(message)
        handler.flush()

        values = {
            'from_header': 'Adam Stein <adam@csh.rit.edu>',
            'subject': 'Member posting when there is a can_post list and member is NOT on it'
        }

        assert len(mail.outbox) == 1
        assert mail.outbox[0].bcc == []
        assert mail.outbox[0].body == EXPECTED_REJECTION.substitute(values)
        assert mail.outbox[0].from_email == 'residents_test-bounces@huntingtonhillsinc.org'
        assert mail.outbox[0].reply_to == []
        assert mail.outbox[0].subject == 'Your message to Residents was rejected'
        assert mail.outbox[0].to == ['Adam Stein <adam@csh.rit.edu>']

        headers = mail.outbox[0].extra_headers
        assert len(headers) == 3
        assert headers['From'] == 'residents_test@huntingtonhillsinc.org'
        assert headers['Sender'] == 'residents_test-bounces@huntingtonhillsinc.org'
        assert headers['X-Sender'] == 'residents_test-bounces@huntingtonhillsinc.org'

        assert getattr(mail.outbox[0], 'alternatives', None) is None

        assert stream.getvalue() == (
            'Adam Stein <adam@csh.rit.edu> is not allowed to post to the Residents list\n'
        )

        msgs = Message.objects.all()
        assert msgs.count() == 1
        assert msgs[0].subject == 'Member posting when there is a can_post list and member is NOT on it'

    def test_valid_email_non_member_posting(self, mailbox, resident_ml, email1, email2, log_stream):
        stream, handler = log_stream

        assert Message.objects.count() == 0

        message = email.message_from_bytes(b'''\
Date: Sun, 20 Jan 2013 11:53:53 -0800
Message-ID: <CAMdmm+hGH8Dgn-_0xnXJCd=PhyNAiouOYm5zFP0z-foqTO60zA@mail.gmail.com>
Subject: Valid Email, Non Member
From: Joe NonMember <joe@nonmember.org>
To: Residents <residents_test@huntingtonhillsinc.org>
Content-Type: text/plain; charset="iso-8859-1"
Content-Transfer-Encoding: 7bit

Generic email text.
''')

        mailbox.process_incoming_message(message)
        handler.flush()

        values = {
            'from_header': 'Joe NonMember <joe@nonmember.org>',
            'subject': 'Valid Email, Non Member'
        }

        assert len(mail.outbox) == 1
        assert mail.outbox[0].bcc == []
        assert mail.outbox[0].body == EXPECTED_REJECTION.substitute(values)
        assert mail.outbox[0].from_email == 'residents_test-bounces@huntingtonhillsinc.org'
        assert mail.outbox[0].reply_to == []
        assert mail.outbox[0].subject == 'Your message to Residents was rejected'
        assert mail.outbox[0].to == ['Joe NonMember <joe@nonmember.org>']

        headers = mail.outbox[0].extra_headers
        assert len(headers) == 3
        assert headers['From'] == 'residents_test@huntingtonhillsinc.org'
        assert headers['Sender'] == 'residents_test-bounces@huntingtonhillsinc.org'
        assert headers['X-Sender'] == 'residents_test-bounces@huntingtonhillsinc.org'

        assert getattr(mail.outbox[0], 'alternatives', None) is None

        assert stream.getvalue() == (
            'Joe NonMember <joe@nonmember.org> is not allowed to post to the Residents list\n'
        )

        msgs = Message.objects.all()
        assert msgs.count() == 1
        assert msgs[0].subject == 'Valid Email, Non Member'

    def test_invalid_email_non_member_posting(self, mailbox, resident_ml, email1, email2, log_stream):
        stream, handler = log_stream

        assert Message.objects.count() == 0

        message = email.message_from_bytes(b'''\
Date: Sun, 20 Jan 2013 11:53:53 -0800
Message-ID: <CAMdmm+hGH8Dgn-_0xnXJCd=PhyNAiouOYm5zFP0z-foqTO60zA@mail.gmail.com>
Subject: Invalid Email, Non Member
From: Spam Email <spam@spamemail.com>
To: Residents <residents_test@huntingtonhillsinc.org>
Content-Type: text/plain; charset="iso-8859-1"
Content-Transfer-Encoding: 7bit

Generic email text.
''')

        mailbox.process_incoming_message(message)
        handler.flush()

        values = {
            'from_header': 'Spam Email <spam@spamemail.com>',
            'subject': 'Invalid Email, Non Member'
        }

        assert len(mail.outbox) == 1
        assert mail.outbox[0].bcc == []
        assert mail.outbox[0].body == EXPECTED_REJECTION.substitute(values)
        assert mail.outbox[0].from_email == 'residents_test-bounces@huntingtonhillsinc.org'
        assert mail.outbox[0].reply_to == []
        assert mail.outbox[0].subject == 'Your message to Residents was rejected'
        assert mail.outbox[0].to == ['Spam Email <spam@spamemail.com>']

        headers = mail.outbox[0].extra_headers
        assert len(headers) == 3
        assert headers['From'] == 'residents_test@huntingtonhillsinc.org'
        assert headers['Sender'] == 'residents_test-bounces@huntingtonhillsinc.org'
        assert headers['X-Sender'] == 'residents_test-bounces@huntingtonhillsinc.org'

        assert getattr(mail.outbox[0], 'alternatives', None) is None

        assert stream.getvalue() == (
            'Spam Email <spam@spamemail.com> is not allowed to post to the Residents list\n'
        )

        msgs = Message.objects.all()
        assert msgs.count() == 1
        assert msgs[0].subject == 'Invalid Email, Non Member'

    def test_sent_message(self, mailbox, resident_ml, email1, email2, log_stream):
        stream, handler = log_stream

        assert Message.objects.count() == 0

        message = email.message_from_bytes(b'''\
Date: Sun, 20 Jan 2013 11:53:53 -0800
Message-ID: <CAMdmm+hGH8Dgn-_0xnXJCd=PhyNAiouOYm5zFP0z-foqTO60zA@mail.gmail.com>
Subject: [Resident] Member posting when no can_post list
From: Adam Stein <adam@csh.rit.edu>
To: Residents <residents_test@huntingtonhillsinc.org>
Content-Type: text/plain; charset="iso-8859-1"
Content-Transfer-Encoding: 7bit
X-Hh-Beenthere: residents_test@huntingtonhillsinc.org

Generic email text.
''')

        mailbox.process_incoming_message(message)
        handler.flush()

        assert len(mail.outbox) == 0
        assert Message.objects.count() == 0

    def test_anonymous_posting(self, mailbox, resident_ml, email1, email2, log_stream):
        stream, handler = log_stream

        assert Message.objects.count() == 0

        resident_ml.allow_anonymous_posts = True
        resident_ml.save()

        message = email.message_from_bytes(b'''\
Date: Sun, 20 Jan 2013 11:53:53 -0800
Message-ID: <CAMdmm+hGH8Dgn-_0xnXJCd=PhyNAiouOYm5zFP0z-foqTO60zA@mail.gmail.com>
Subject: Allow anonymous posting
From: Outsider <outsider@outside.com>
To: Residents <residents_test@huntingtonhillsinc.org>
Content-Type: text/plain; charset="iso-8859-1"
Content-Transfer-Encoding: 7bit

Generic email text.
''')

        mailbox.process_incoming_message(message)
        handler.flush()

        assert len(mail.outbox) == 1
        assert mail.outbox[0].bcc == ['adam@csh.rit.edu', 'randy@member.org']
        assert mail.outbox[0].body == 'Generic email text.'
        assert mail.outbox[0].from_email == (
            'Outsider <outsider@outside.com> via Residents <residents_test@huntingtonhillsinc.org>'
        )
        assert mail.outbox[0].reply_to == ['Outsider <outsider@outside.com>']
        assert mail.outbox[0].subject == '[Residents] Allow anonymous posting'
        assert mail.outbox[0].to == ['Residents <residents_test@huntingtonhillsinc.org>']

        headers = mail.outbox[0].extra_headers
        assert len(headers) == 11
        assert headers['From'] == (
            'Outsider <outsider@outside.com> via Residents <residents_test@huntingtonhillsinc.org>'
        )
        assert headers['List-Archive'] == '<http://smeg:8002/mailing_lists/archives/list/>'
        assert headers['List-Help'] == (
            f'<http://smeg:8002/mailing_lists/lists/>,'
            f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=help%20Residents>'
        )
        assert headers['List-Owner'] == f'<mailto:{settings.DEFAULT_FROM_EMAIL}> (Contact Person for Help)'
        assert headers['List-Post'] == '<mailto:residents_test@huntingtonhillsinc.org>'
        assert headers['List-Subscribe'] == (
            f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=subscribe%20Residents>'
        )
        assert headers['List-Unsubscribe'] == (
            f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=unsubscribe%20Residents>'
        )
        assert headers['Message-ID'] == message._headers[1][1]
        assert headers['Sender'] == 'Residents <residents_test-bounces@huntingtonhillsinc.org>'
        assert headers['X-Hh-Beenthere'] == 'residents_test@huntingtonhillsinc.org'
        assert headers['X-Sender'] == 'Residents <residents_test-bounces@huntingtonhillsinc.org>'

        assert len(mail.outbox[0].alternatives) == 0

        assert stream.getvalue() == ''

        msgs = Message.objects.all()
        assert msgs.count() == 1
        assert msgs[0].subject == '[Residents] Allow anonymous posting'

    def test_reply_subject_line(self, mailbox, resident_ml, email1, email2, log_stream):
        stream, handler = log_stream

        assert Message.objects.count() == 0

        message = email.message_from_bytes(b'''\
Date: Sun, 20 Jan 2013 11:53:53 -0800
Message-ID: <CAMdmm+hGH8Dgn-_0xnXJCd=PhyNAiouOYm5zFP0z-foqTO60zA@mail.gmail.com>
Subject: Re: [Residents] Re: Check reply subject line
From: Adam Stein <adam@csh.rit.edu>
To: Residents <residents_test@huntingtonhillsinc.org>
Content-Type: text/plain; charset="iso-8859-1"
Content-Transfer-Encoding: 7bit

Generic email text.
''')

        mailbox.process_incoming_message(message)
        handler.flush()

        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == '[Residents] Re: Check reply subject line'

        assert stream.getvalue() == ''

        msgs = Message.objects.all()
        assert msgs.count() == 1
        assert msgs[0].subject == '[Residents] Re: Check reply subject line'

    def test_sanitize_html(self, mailbox, resident_ml, email1, email2, log_stream):
        stream, handler = log_stream

        assert Message.objects.count() == 0

        message = email.message.EmailMessage()
        message['From'] = 'Adam Stein <adam@csh.rit.edu>'
        message['To'] = 'Residents <residents_test@huntingtonhillsinc.org>'
        message['Subject'] = 'Sanitize the HTML'
        message['Message-ID'] = '<CAMdmm+hGH8Dgn-_0xnXJCd=PhyNAiouOYm5zFP0z-foqTO60zA@mail.gmail.com>'
        message.set_content('This email has HTML')
        message.add_alternative(
            """
                <html>
                    <body>
                        <p>This email has <strong>HTML</strong>.</p>

                        <p>Link to http://www.google.com/</p>

                        <p>Link to <a href="http://www.huntingtonhillsinc.org/">Huntington Hills</a>.</p>

                        <script>evil()</script>

                        <img src="image.gif" onerror="evil()">

                        mailto:adam@csh.rit.edu
                    </body>
                </html>
            """,
            subtype='html'
        )

        mailbox.process_incoming_message(message)
        handler.flush()

        assert len(mail.outbox) == 1
        assert mail.outbox[0].bcc == ['adam@csh.rit.edu', 'randy@member.org']
        assert mail.outbox[0].body == 'This email has HTML'
        assert mail.outbox[0].from_email == 'Adam Stein via Residents <residents_test@huntingtonhillsinc.org>'
        assert mail.outbox[0].reply_to == ['Adam Stein <adam@csh.rit.edu>']
        assert mail.outbox[0].subject == '[Residents] Sanitize the HTML'
        assert mail.outbox[0].to == ['Residents <residents_test@huntingtonhillsinc.org>']

        headers = mail.outbox[0].extra_headers
        assert len(headers) == 11
        assert headers['From'] == 'Adam Stein via Residents <residents_test@huntingtonhillsinc.org>'
        assert headers['List-Archive'] == '<http://smeg:8002/mailing_lists/archives/list/>'
        assert headers['List-Help'] == (
            f'<http://smeg:8002/mailing_lists/lists/>,'
            f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=help%20Residents>'
        )
        assert headers['List-Owner'] == f'<mailto:{settings.DEFAULT_FROM_EMAIL}> (Contact Person for Help)'
        assert headers['List-Post'] == '<mailto:residents_test@huntingtonhillsinc.org>'
        assert headers['List-Subscribe'] == (
            f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=subscribe%20Residents>'
        )
        assert headers['List-Unsubscribe'] == (
            f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=unsubscribe%20Residents>'
        )
        assert headers['Message-ID'] == message['Message-ID']
        assert headers['Sender'] == 'Residents <residents_test-bounces@huntingtonhillsinc.org>'
        assert headers['X-Hh-Beenthere'] == 'residents_test@huntingtonhillsinc.org'
        assert headers['X-Sender'] == 'Residents <residents_test-bounces@huntingtonhillsinc.org>'

        alternatives = mail.outbox[0].alternatives
        assert len(alternatives) == 1
        assert alternatives[0][0] == (
            '<html>                    <body>                        '
            '<p>This email has <strong>HTML</strong>.</p>                        '
            '<p>Link to <a href="http://www.google.com/">http://www.google.com/</a></p>                        '
            '<p>Link to <a href="http://www.huntingtonhillsinc.org/">Huntington Hills</a>.</p>                                                '
            '<img src="image.gif">                        '
            '<a href="mailto:adam@csh.rit.edu">adam@csh.rit.edu</a>                    </body>                </html>'
        )
        assert alternatives[0][1] == 'text/html'

        assert stream.getvalue() == ''

        msgs = Message.objects.all()
        assert msgs.count() == 1
        assert msgs[0].subject == '[Residents] Sanitize the HTML'
