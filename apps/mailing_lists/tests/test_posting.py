import email
from io import StringIO
import logging

from django.core import mail
from django.test import TestCase

from django_mailbox.models import Mailbox, Message

from residents.models import Person

from ..models import MailingList


class PostingTest(TestCase):
    fixtures = [
        'apps/mailing_lists/tests/fixtures/streets.json',
        'apps/mailing_lists/tests/fixtures/property_types.json',
        'apps/mailing_lists/tests/fixtures/properties.json',
        'apps/mailing_lists/tests/fixtures/people.json',
        'apps/mailing_lists/tests/fixtures/email_types.json',
        'apps/mailing_lists/tests/fixtures/emails.json'
    ]

    def setUp(self):
        self.mailbox = Mailbox.objects.create(name='Residents')
        self.resident_ml = MailingList.objects.create(
            email='residents_test@huntingtonhillsinc.org',
            email_type=EmailType.objects.get(email_type=EmailType.RESIDENT),
            mailbox=self.mailbox
        )

        person1 = Person.objects.get(first_name='Adam', last_name='Stein')
        person2 = Person.objects.get(first_name='Randy', last_name='Member')

        self.resident_ml.members.add(person1)
        self.resident_ml.members.add(person2)

        logging.disable(logging.NOTSET)  # Normally logging is turned off for unit tests, turn it back on
        self.stream = StringIO()
        self.string_handler = logging.StreamHandler(self.stream)
        log = logging.getLogger('mailing_lists')
        log.setLevel(logging.INFO)
        for handler in log.handlers:
            log.removeHandler(handler)
        log.addHandler(self.string_handler)

    def test_no_can_post_list(self):
        self.assertEqual(0, Message.objects.count())

        message =  email.message_from_bytes(b'''\
Date: Sun, 20 Jan 2013 11:53:53 -0800
Message-ID: <CAMdmm+hGH8Dgn-_0xnXJCd=PhyNAiouOYm5zFP0z-foqTO60zA@mail.gmail.com>
Subject: Member posting when no can_post list
From: Adam Stein <adam@csh.rit.edu>
To: Residents <residents_test@huntingtonhillsinc.org>
Content-Type: text/plain; charset="iso-8859-1"
Content-Transfer-Encoding: 7bit

Generic email text.
''')

        self.mailbox.process_incoming_message(message)
        self.string_handler.flush()

        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(['randy@member.org', 'adam@csh.rit.edu'], mail.outbox[0].bcc)
        self.assertEqual('Generic email text.', mail.outbox[0].body)
        self.assertEqual('Adam Stein via Residents <residents_test@huntingtonhillsinc.org>', mail.outbox[0].from_email)
        self.assertEqual(['Adam Stein <adam@csh.rit.edu>'], mail.outbox[0].reply_to)
        self.assertEqual('[Residents] Member posting when no can_post list', mail.outbox[0].subject)
        self.assertEqual(['Residents <residents_test@huntingtonhillsinc.org>'], mail.outbox[0].to)

        headers = mail.outbox[0].extra_headers
        self.assertEqual(11, len(headers))
        self.assertEqual('Adam Stein via Residents <residents_test@huntingtonhillsinc.org>', headers['From'])
        self.assertEqual('<http://smeg:8002/mailing_lists/archives/list/>', headers['List-Archive'])
        self.assertEqual(
            '<http://www.huntingtonhillsinc.org/members/mailing_lists.html>,<mailto:adam@csh.rit.edu'
            '?subject=help%20Residents>',
            headers['List-Help']
        )
        self.assertEqual('<mailto:adam@csh.rit.edu> (Contact Person for Help)', headers['List-Owner'])
        self.assertEqual('<mailto:residents_test@huntingtonhillsinc.org>', headers['List-Post'])
        self.assertEqual('<mailto:adam@csh.rit.edu?subject=subscribe%20Residents>', headers['List-Subscribe'])
        self.assertEqual('<mailto:adam@csh.rit.edu?subject=unsubscribe%20Residents>', headers['List-Unsubscribe'])
        # noinspection PyUnresolvedReferences
        self.assertEqual(message._headers[1][1], headers['Message-ID'])
        self.assertEqual('Residents <residents_test-bounces@huntingtonhillsinc.org>', headers['Sender'])
        self.assertEqual('residents_test@huntingtonhillsinc.org', headers['X-Hh-Beenthere'])
        self.assertEqual('Residents <residents_test-bounces@huntingtonhillsinc.org>', headers['X-Sender'])

        # noinspection PyUnresolvedReferences
        self.assertEqual(0, len(mail.outbox[0].alternatives))

        self.assertEqual('', self.stream.getvalue())

        msgs = Message.objects.all()
        self.assertEqual(1, msgs.count())
        self.assertEqual('[Residents] Member posting when no can_post list', msgs[0].subject)

    def test_valid_email_non_member_posting(self):
        self.assertEqual(0, Message.objects.count())

        message =  email.message_from_bytes(b'''\
Date: Sun, 20 Jan 2013 11:53:53 -0800
Message-ID: <CAMdmm+hGH8Dgn-_0xnXJCd=PhyNAiouOYm5zFP0z-foqTO60zA@mail.gmail.com>
Subject: Valid Email, Non Member
From: Joe NonMember <joe@nonmember.org>
To: Residents <residents_test@huntingtonhillsinc.org>
Content-Type: text/plain; charset="iso-8859-1"
Content-Transfer-Encoding: 7bit

Generic email text.
''')

        self.mailbox.process_incoming_message(message)
        self.string_handler.flush()

        self.assertEqual(1, len(mail.outbox))
        self.assertEqual([], mail.outbox[0].bcc)
        self.assertEqual('You are not authorized', mail.outbox[0].body)
        self.assertEqual('residents_test-bounces@huntingtonhillsinc.org', mail.outbox[0].from_email)
        self.assertEqual([], mail.outbox[0].reply_to)
        self.assertEqual('Email Rejected', mail.outbox[0].subject)
        self.assertEqual(['Joe NonMember <joe@nonmember.org>'], mail.outbox[0].to)

        headers = mail.outbox[0].extra_headers
        self.assertEqual(3, len(headers))
        self.assertEqual('residents_test@huntingtonhillsinc.org', headers['From'])
        self.assertEqual('residents_test-bounces@huntingtonhillsinc.org', headers['Sender'])
        self.assertEqual('residents_test-bounces@huntingtonhillsinc.org', headers['X-Sender'])

        self.assertIsNone(getattr(mail.outbox[0], 'alternatives', None))

        self.assertEqual(
            'Joe NonMember <joe@nonmember.org> is not allowed to post to the Residents list\n',
            self.stream.getvalue()
        )

        msgs = Message.objects.all()
        self.assertEqual(1, msgs.count())
        self.assertEqual('Valid Email, Non Member', msgs[0].subject)

    def test_invalid_email_non_member_posting(self):
        self.assertEqual(0, Message.objects.count())

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

        self.mailbox.process_incoming_message(message)
        self.string_handler.flush()

        self.assertEqual(1, len(mail.outbox))
        self.assertEqual([], mail.outbox[0].bcc)
        self.assertEqual('You are not authorized', mail.outbox[0].body)
        self.assertEqual('residents_test-bounces@huntingtonhillsinc.org', mail.outbox[0].from_email)
        self.assertEqual([], mail.outbox[0].reply_to)
        self.assertEqual('Email Rejected', mail.outbox[0].subject)
        self.assertEqual(['Spam Email <spam@spamemail.com>'], mail.outbox[0].to)

        headers = mail.outbox[0].extra_headers
        self.assertEqual(3, len(headers))
        self.assertEqual('residents_test@huntingtonhillsinc.org', headers['From'])
        self.assertEqual('residents_test-bounces@huntingtonhillsinc.org', headers['Sender'])
        self.assertEqual('residents_test-bounces@huntingtonhillsinc.org', headers['X-Sender'])

        self.assertIsNone(getattr(mail.outbox[0], 'alternatives', None))

        self.assertEqual(
            'Spam Email <spam@spamemail.com> is not allowed to post to the Residents list\n',
            self.stream.getvalue()
        )

        msgs = Message.objects.all()
        self.assertEqual(1, msgs.count())
        self.assertEqual('Invalid Email, Non Member', msgs[0].subject)

    def test_sent_message(self):
        # Already processed messages that are back in the mailbox (because they are mailed to that mailbox) are 
        # silently removed
        
        self.assertEqual(0, Message.objects.count())

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

        self.mailbox.process_incoming_message(message)
        self.string_handler.flush()

        self.assertEqual(0, len(mail.outbox))
        self.assertEqual(0, Message.objects.count())

    def test_anonymous_posting(self):
        logging.disable(logging.NOTSET)  # Normally logging is turned off for unit tests, turn it back on
        stream = StringIO()
        string_handler = logging.StreamHandler(stream)
        log = logging.getLogger('mailing_lists')
        log.setLevel(logging.INFO)
        for handler in log.handlers:
            log.removeHandler(handler)
        log.addHandler(string_handler)

        self.assertEqual(0, Message.objects.count())

        self.resident_ml.allow_anonymous_posts = True
        self.resident_ml.save()

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

        self.mailbox.process_incoming_message(message)
        string_handler.flush()

        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(['randy@member.org', 'adam@csh.rit.edu'], mail.outbox[0].bcc)
        self.assertEqual('Generic email text.', mail.outbox[0].body)
        self.assertEqual(
            'Outsider <outsider@outside.com> via Residents <residents_test@huntingtonhillsinc.org>',
            mail.outbox[0].from_email
        )
        self.assertEqual(['Outsider <outsider@outside.com>'], mail.outbox[0].reply_to)
        self.assertEqual('[Residents] Allow anonymous posting', mail.outbox[0].subject)
        self.assertEqual(['Residents <residents_test@huntingtonhillsinc.org>'], mail.outbox[0].to)

        headers = mail.outbox[0].extra_headers
        self.assertEqual(11, len(headers))
        self.assertEqual(
            'Outsider <outsider@outside.com> via Residents <residents_test@huntingtonhillsinc.org>',
            headers['From']
        )
        self.assertEqual('<http://smeg:8002/mailing_lists/archives/list/>', headers['List-Archive'])
        self.assertEqual(
            '<http://www.huntingtonhillsinc.org/members/mailing_lists.html>,<mailto:adam@csh.rit.edu'
            '?subject=help%20Residents>',
            headers['List-Help']
        )
        self.assertEqual('<mailto:adam@csh.rit.edu> (Contact Person for Help)', headers['List-Owner'])
        self.assertEqual('<mailto:residents_test@huntingtonhillsinc.org>', headers['List-Post'])
        self.assertEqual('<mailto:adam@csh.rit.edu?subject=subscribe%20Residents>', headers['List-Subscribe'])
        self.assertEqual('<mailto:adam@csh.rit.edu?subject=unsubscribe%20Residents>', headers['List-Unsubscribe'])
        # noinspection PyUnresolvedReferences
        self.assertEqual(message._headers[1][1], headers['Message-ID'])
        self.assertEqual('Residents <residents_test-bounces@huntingtonhillsinc.org>', headers['Sender'])
        self.assertEqual('residents_test@huntingtonhillsinc.org', headers['X-Hh-Beenthere'])
        self.assertEqual('Residents <residents_test-bounces@huntingtonhillsinc.org>', headers['X-Sender'])

        # noinspection PyUnresolvedReferences
        self.assertEqual(0, len(mail.outbox[0].alternatives))

        self.assertEqual('', self.stream.getvalue())

        msgs = Message.objects.all()
        self.assertEqual(1, msgs.count())
        self.assertEqual('[Residents] Allow anonymous posting', msgs[0].subject)

    def test_repy_subject_line(self):
        self.assertEqual(0, Message.objects.count())

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

        self.mailbox.process_incoming_message(message)
        self.string_handler.flush()

        self.assertEqual(1, len(mail.outbox))
        self.assertEqual('[Residents] Re: Check reply subject line', mail.outbox[0].subject)

        self.assertEqual('', self.stream.getvalue())

        msgs = Message.objects.all()
        self.assertEqual(1, msgs.count())
        self.assertEqual('[Residents] Re: Check reply subject line', msgs[0].subject)

    def test_sanitize_html(self):
        self.assertEqual(0, Message.objects.count())

        message = email.message_from_bytes(b'''\
Date: Sun, 20 Jan 2013 11:53:53 -0800
Message-ID: <CAMdmm+hGH8Dgn-_0xnXJCd=PhyNAiouOYm5zFP0z-foqTO60zA@mail.gmail.com>
Subject: Sanitize the HTML
From: Adam Stein <adam@csh.rit.edu>
To: Residents <residents_test@huntingtonhillsinc.org>
Content-Type: text/plain; charset="iso-8859-1"
Content-Transfer-Encoding: 7bit

This email has HTML
''')

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

        self.mailbox.process_incoming_message(message)
        self.string_handler.flush()

        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(['randy@member.org', 'adam@csh.rit.edu'], mail.outbox[0].bcc)
        self.assertEqual('This email has HTML', mail.outbox[0].body)
        self.assertEqual('Adam Stein via Residents <residents_test@huntingtonhillsinc.org>', mail.outbox[0].from_email)
        self.assertEqual(['Adam Stein <adam@csh.rit.edu>'], mail.outbox[0].reply_to)
        self.assertEqual('[Residents] Sanitize the HTML', mail.outbox[0].subject)
        self.assertEqual(['Residents <residents_test@huntingtonhillsinc.org>'], mail.outbox[0].to)

        headers = mail.outbox[0].extra_headers
        self.assertEqual(11, len(headers))
        self.assertEqual('Adam Stein via Residents <residents_test@huntingtonhillsinc.org>', headers['From'])
        self.assertEqual('<http://smeg:8002/mailing_lists/archives/list/>', headers['List-Archive'])
        self.assertEqual(
            '<http://www.huntingtonhillsinc.org/members/mailing_lists.html>,<mailto:adam@csh.rit.edu'
            '?subject=help%20Residents>',
            headers['List-Help']
        )
        self.assertEqual('<mailto:adam@csh.rit.edu> (Contact Person for Help)', headers['List-Owner'])
        self.assertEqual('<mailto:residents_test@huntingtonhillsinc.org>', headers['List-Post'])
        self.assertEqual('<mailto:adam@csh.rit.edu?subject=subscribe%20Residents>', headers['List-Subscribe'])
        self.assertEqual('<mailto:adam@csh.rit.edu?subject=unsubscribe%20Residents>', headers['List-Unsubscribe'])
        # noinspection PyUnresolvedReferences
        self.assertEqual(message['Message-ID'], headers['Message-ID'])
        self.assertEqual('Residents <residents_test-bounces@huntingtonhillsinc.org>', headers['Sender'])
        self.assertEqual('residents_test@huntingtonhillsinc.org', headers['X-Hh-Beenthere'])
        self.assertEqual('Residents <residents_test-bounces@huntingtonhillsinc.org>', headers['X-Sender'])

        # noinspection PyUnresolvedReferences
        alternatives = mail.outbox[0].alternatives
        self.assertEqual(1, len(alternatives))
        self.assertEqual(
            '<html>                    <body>                        '
            '<p>This email has <strong>HTML</strong>.</p>                                                '
            '<p>Link to <a href="http://www.google.com/">http://www.google.com/</a></p>'
            '                                                '
            '<p>Link to <a href="http://www.huntingtonhillsinc.org/">Huntington Hills</a>.</p>'
            '                                                                                                '
            '<img src="image.gif">                                                '
            '<a href="mailto:adam@csh.rit.edu">adam@csh.rit.edu</a>                    </body>                </html>',
            alternatives[0][0]
        )
        self.assertEqual('text/html', alternatives[0][1])

        self.assertEqual('', self.stream.getvalue())

        msgs = Message.objects.all()
        self.assertEqual(1, msgs.count())
        self.assertEqual('[Residents] Sanitize the HTML', msgs[0].subject)


    def tearDown(self):
        # Turn logging back off (only show critical messages)
        logging.disable(logging.CRITICAL)
