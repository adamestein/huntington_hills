from django.contrib import admin
from django.contrib.messages import success

from django_mailbox.utils import convert_header_to_unicode

from library.admin import custom_title_filter_factory

from residents.models import Board, BoardTerm

from .models import MailingList, RejectedMessage


@admin.register(MailingList)
class MailingListAdmin(admin.ModelAdmin):
    actions = ['set_can_post_to_board_members']
    filter_horizontal = ('can_post', 'members',)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def set_can_post_to_board_members(self, request, queryset):
        board = Board.objects.all()[0]
        board_members = []

        for position in BoardTerm.POSITIONS:
            office = position[1].lower().replace(' ', '_')
            board_members.append(getattr(board, office))

        # For every selected ML, delete ALL the items in can_post and add all current board members
        for mailing_list in queryset:
            mailing_list.can_post.clear()
            mailing_list.can_post.add(*board_members)

        success(request, 'Mailing List(s) have been updated')

    set_can_post_to_board_members.short_description = 'Set "can post" list to board members'

@admin.register(RejectedMessage)
class RejectedMessageAdmin(admin.ModelAdmin):
    list_display = (
        'get_subject',
        'get_mailbox',
        'get_sender',
        'get_processed'
    )
    list_filter = (
        ('message__mailbox', custom_title_filter_factory(admin.RelatedFieldListFilter, 'Mailbox')),
    )

    def get_mailbox(self, msg):
        return msg.message.mailbox
    get_mailbox.admin_order_field = 'message__mailbox'
    get_mailbox.short_description = 'Mailbox'

    def get_processed(self, msg):
        return msg.message.processed
    get_processed.admin_order_field = 'message__processed'
    get_processed.short_description = 'Processed'

    def get_sender(self, msg):
        return msg.message.from_header
    get_sender.admin_order_field = 'message__from_header'
    get_sender.short_description = 'Sender'

    def get_subject(self, msg):
        return convert_header_to_unicode(msg.message.subject)
    get_subject.admin_order_field = 'message__subject'
    get_subject.short_description = 'SUBJECT'
