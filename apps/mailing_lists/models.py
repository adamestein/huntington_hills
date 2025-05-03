import logging
import re

from django.conf import settings
from django.core.mail import BadHeaderError, EmailMessage, EmailMultiAlternatives, get_connection
from django.db import models
from django.dispatch import receiver
from django.shortcuts import reverse
from django.template.defaultfilters import pluralize
from django.utils.text import slugify

import upsilonconf

from lxml.html.clean import Cleaner, autolink_html

from django_mailbox.models import Mailbox, Message
from django_mailbox.signals import message_received

from residents.models import Email

logger = logging.getLogger(__name__)


# We use the same cleaner for every message with HTML, so only create this once
cleaner = Cleaner(
    add_nofollow=False,
    annoying_tags=True,
    comments=True,
    embedded=True,
    forms=True,
    frames=True,
    javascript=True,
    page_structure=False,
    processing_instructions=True,
    remove_unknown_tags=True,
    safe_attrs_only=True,
    scripts=True
)


class MailingList(models.Model):
    allow_anonymous_posts = models.BooleanField(default=False)
    can_post = models.ManyToManyField(Email, blank=True, related_name='can_post')    # If empty, all members can post
    email = models.EmailField()
    mailbox = models.OneToOneField(Mailbox)
    members = models.ManyToManyField(Email, related_name='members')
    name_slug = models.SlugField()

    class Meta:
        ordering = ('mailbox__name',)

    @property
    def bounce_email(self):
        pieces = self.email.split('@')
        return f'{pieces[0]}-bounces@{pieces[1]}'

    def member(self, email):
        try:
            return self.members.get(email=email).personemail.person
        except Email.DoesNotExist:
            return None

    def member_can_post(self, email):
        return self.can_post.count() == 0 or self.can_post.filter(email=email).exists()

    @property
    def owner_email(self):
        pieces = self.email.split('@')
        return f'{pieces[0]}-owner@{pieces[1]}'

    def save(self, *args, **kwargs):
        self.name_slug = slugify(self.mailbox.name)
        super().save(*args, **kwargs)

    def __str__(self):
        num_members = self.members.count()
        num_can_post = self.can_post.count()
        if self.allow_anonymous_posts:
            can_post = 'anonymous posts allowed'
        elif num_can_post == 0:
            can_post = 'all members can post'
        else:
            can_post = f'{num_can_post} member{pluralize(num_can_post)} can post'
        return f'{self.mailbox.name} ({num_members} member{pluralize(num_members)}, {can_post})'


class RejectedMessage(models.Model):
    message = models.OneToOneField(Message, on_delete=models.CASCADE)

    def __str__(self):
        return self.message.subject


@receiver(message_received)
def send(sender, message, **_):
    try:
        mailing_list = sender.mailinglist
    except AttributeError:
        # Probably a re-send of the message received signal in Django Admin, can ignore
        pass
    else:
        email_object = message.get_email_object()

        if email_object.get('X-Hh-Beenthere') == mailing_list.email:
            # This was the message that was sent out, don't need to store the one sent back to the ML
            message.delete()
        else:
            member = mailing_list.member(message.from_address[0])

            # We allow posting to this mailing list if:
            #
            #   1) the sender is not in the system at all and the ML allows anonymous posts
            #   2) the sender is a member of this ML and there is no can_post list (all and only members can post)
            #   3) the sender is on the can_post list
            if member:
                can_post = mailing_list.member_can_post(message.from_address[0])
            else:
                can_post = mailing_list.allow_anonymous_posts


            config = upsilonconf.load('.env.json')['Mailing Lists']

            connection_args = {
                'host': config.host,
                'password': config.credentials[sender.name]['password'],
                'port': config.port,
                'use_tls': True,
                'username': config.credentials[sender.name]['username']
            }

            if can_post:
                if member:
                    from_email = f'{member.full_name} via {sender.name} <{mailing_list.email}>'
                else:
                    from_email = f'{message.from_header} via {sender.name} <{mailing_list.email}>'

                # Remove any [ML NAME], Re: strings, and newlines
                subject = (
                    re.sub(r'(?<!^)(?i)Re: ', '', message.subject.replace(f'[{sender.name}] ', ''), flags=re.M)
                    .replace('\r', '')
                    .replace('\n', '')
                )
                subject = f'[{sender.name}] {subject}'

                message.subject = subject
                message.save()

                with get_connection(**connection_args) as connection:
                    msg = EmailMultiAlternatives(
                        bcc=[member.email for member in mailing_list.members.all()],
                        body=message.text,
                        connection=connection,
                        from_email=from_email,
                        headers={
                            'From': from_email,
                            'List-Archive': f'<{settings.SITE_URL}{reverse("mailing_lists:archive_list")}>',
                            'List-Help': (
                                f'<{settings.SITE_URL}{reverse("mailing_lists:lists")}>,'
                                f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=help%20{sender.name}>'
                            ),
                            'List-Owner': f'<mailto:{settings.DEFAULT_FROM_EMAIL}> (Contact Person for Help)',
                            'List-Post': f'<mailto:{mailing_list.email}>',
                            'List-Subscribe': f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=subscribe%20{sender.name}>',
                            'List-Unsubscribe': f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=unsubscribe%20{sender.name}>',
                            'Message-ID': message.message_id,
                            'Sender': f'{sender.name} <{mailing_list.bounce_email}>',
                            'X-Hh-Beenthere': mailing_list.email,
                            'X-Sender': f'{sender.name} <{mailing_list.bounce_email}>'
                        },
                        reply_to=(message.from_header,),
                        subject=subject,
                        to=[f'{sender.name} <{mailing_list.email}>']
                    )

                    if email_object.get('In-Reply-to') is not None:
                        msg.extra_headers['In-Reply-To'] = email_object['In-Reply-to']

                    if email_object.get('References') is not None:
                        msg.extra_headers['References'] = \
                            email_object['References'].replace('\r\n', ' ').replace('\n', '')

                    if message.html:
                        msg.attach_alternative(autolink_html(cleaner.clean_html(message.html)), 'text/html')

                    for att in message.attachments.all():
                        # noinspection PyProtectedMember
                        msg.attach(
                            filename=att.get_filename(), content=att.document.read(),
                            mimetype=att._get_rehydrated_headers().get_content_type()
                        )

                    try:
                        msg.send()
                    except BadHeaderError as e:
                        logger.error(f'Error sending rejection email with subject "{subject}": {e}')
            else:
                # Save the message to our reject pile (easier to view just rejected messages or to remove when
                # viewing ML archives)
                RejectedMessage.objects.create(message=message)

                # Log the issue and respond
                logger.info(f'{message.from_header} is not allowed to post to the {sender.name} list')

                msg = f'''\
Dear {message.from_header},

Your message to the {sender.name} list has been automatically rejected.

You are not authorized to post to this mailing list because your email
address is not subscribed. This list only accepts posts from subscribed
members.

If you believe this is incorrect, or you would like to request permission
to post, please contact the list administrator at:

{mailing_list.owner_email}

-----------------------------------------------------------------------

Reason for rejection:

Post by non-member to a members-only list.

---------------------------------------------------------------

Original message information:

Subject: {message.subject}

{message.text}
'''

                with get_connection(**connection_args) as connection:
                    msg = EmailMessage(
                        body=msg,
                        connection=connection,
                        from_email=mailing_list.bounce_email,
                        headers={
                            'From': mailing_list.email,
                            'Sender': mailing_list.bounce_email,
                            'X-Sender': mailing_list.bounce_email
                        },
                        subject=f'Your message to {sender.name} was rejected',
                        to=[message.from_header]
                    )

                    try:
                        msg.send()
                    except Exception as e:
                        logger.error(f'Error sending rejection email to "{message.from_header}": {e}')
