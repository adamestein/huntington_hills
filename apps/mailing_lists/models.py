import logging
import re

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.db import models
from django.dispatch import receiver
from django.shortcuts import reverse
from django.template.defaultfilters import pluralize

from django_mailbox.models import Mailbox, Message
from django_mailbox.signals import message_received

from residents.models import Email, EmailType, Person

logger = logging.getLogger(__name__)


class MailingList(models.Model):
    allow_anonymous_posts = models.BooleanField(default=False)
    can_post = models.ManyToManyField(Person, blank=True, related_name='can_post')    # If empty, all members can post
    email = models.EmailField()
    email_type = models.ForeignKey(EmailType)
    mailbox = models.OneToOneField(Mailbox)
    members = models.ManyToManyField(Person, related_name='members')

    @property
    def bounce_email(self):
        pieces = self.email.split('@')
        return f'{pieces[0]}-bounces@{pieces[1]}'

    def __str__(self):
        num_members = self.members.count()
        return f'{self.mailbox.name} ({num_members} member{pluralize(num_members)})'


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
            try:
                member = Email.objects.get(email=message.from_address[0], email_type=mailing_list.email_type).person
            except (Email.DoesNotExist, IndexError):
                member = None

            # We allow posting to this mailing list if:
            #
            #   1) the sender is not in the system at all and the ML allows anonymous posts
            #   2) the sender is a member of this ML and there is no can_post list (all and only members can post)
            #   3) the sender is on the can_post list

            if member:
                can_post = mailing_list.can_post.count() == 0 and member.members.filter().exists() or \
                           member.can_post.filter().exists()
            else:
                can_post = mailing_list.allow_anonymous_posts

            if can_post:
                bcc_list = []
                for person in mailing_list.members.all():
                    bcc_list += list(person.emails.filter(email_type=mailing_list.email_type))

                if member:
                    from_email = f'{member.full_name} via {sender.name} <{mailing_list.email}>'
                else:
                    from_email = f'{message.from_header} via {sender.name} <{mailing_list.email}>'

                # Remove any [ML NAME] and Re: strings
                subject = re.sub(r'(?<!^)(?i)Re: ', '', message.subject.replace(f'[{sender.name}] ', ''), flags=re.M)
                subject = f'[{sender.name}] {subject}'

                message.subject = subject
                message.save()

                msg = EmailMultiAlternatives(
                    bcc=bcc_list,
                    body=message.text,
                    from_email=from_email,
                    headers={
                        'From': from_email,
                        'List-Archive': f'<{settings.SITE_URL}{reverse("mailing_lists:archive_list")}>',
                        'List-Help': (
                            '<http://www.huntingtonhillsinc.org/members/mailing_lists.html>,'
                            f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=help%20{sender.name}>'
                        ),
                        'List-Owner': f'<mailto:{settings.DEFAULT_FROM_EMAIL}> (Contact Person for Help)',
                        'List-Post': '<mailto:residents_test@huntingtonhillsinc.org>',
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
                    msg.extra_headers['References'] = email_object['References'].replace('\r\n\t', ' ')

                if message.html:
                    msg.attach_alternative(message.html, 'text/html')

                for att in message.attachments.all():
                    # noinspection PyProtectedMember
                    msg.attach(
                        filename=att.get_filename(), content=att.document.read(),
                        mimetype=att._get_rehydrated_headers().get_content_type()
                    )

                msg.send()
            else:
                # Save the message to our reject pile (easier to view just rejected messages or to remove when
                # viewing ML archives)
                RejectedMessage.objects.create(message=message)

                # Log the issue and respond
                logger.info(f'{message.from_header} is not allowed to post to the {sender.name} list')

                msg = EmailMessage(
                    body='You are not authorized',
                    from_email=mailing_list.bounce_email,
                    headers={
                        'From': mailing_list.email,
                        'Sender': mailing_list.bounce_email,
                        'X-Sender': mailing_list.bounce_email
                    },
                    subject='Email Rejected',
                    to=[message.from_header]
                )
                msg.send()



