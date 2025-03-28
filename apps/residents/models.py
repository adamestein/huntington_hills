# noinspection PyPackageRequirements
from localflavor.us.models import USStateField

from phonenumber_field.modelfields import PhoneNumberField

from django.db import models

from library.models import SingletonModel


class Board(SingletonModel):
    director_at_large_1 = models.ForeignKey('Person', blank=True, related_name='director_at_large_1')
    director_at_large_2 = models.ForeignKey('Person', blank=True, related_name='director_at_large_2')
    president = models.ForeignKey('Person', blank=True, related_name='president')
    secretary = models.ForeignKey('Person', blank=True, related_name='secretary')
    treasurer = models.ForeignKey('Person', blank=True, related_name='treasurer')
    vice_president = models.ForeignKey('Person', blank=True, related_name='vice_president')

    class Meta:
        verbose_name_plural = 'Board members'

    def get_email_list(self):
        emails = []
        for field in self._meta.get_fields():
            if not field.primary_key:
                # We assume the first email is the one to be used
                emails.append(getattr(self, field.name).emails.first().email)
        return emails


class BoardTerm(models.Model):
    POSITIONS = (
        ('d1', 'Director at Large 1'),
        ('d2', 'Director at Large 2'),
        ('p', 'President'),
        ('s', 'Secretary'),
        ('t', 'Treasurer'),
        ('vp', 'Vice President')
    )

    elected_date = models.DateField()
    office = models.CharField(choices=POSITIONS, max_length=2)
    person = models.ForeignKey('Person')

    class Meta:
        ordering = ('-elected_date', 'person')

    @staticmethod
    def office_abbr(office):
        abbrs = {
            'director_at_large_1': 'd1',
            'director_at_large_2': 'd2',
            'president': 'p',
            'secretary': 's',
            'treasurer': 't',
            'vice_president': 'vp'
        }
        return abbrs[office]

    def __str__(self):
        return f'[{self.elected_date}] {self.person.full_name} ({self.get_office_display()})'


class Email(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class LotNumber(models.Model):
    lot_number = models.CharField(blank=True, max_length=20, null=True)
    property = models.ForeignKey('Property')

    class Meta:
        ordering = ('property', 'lot_number')
        unique_together = ('lot_number', 'property')

    def __str__(self):
        return f'({self.lot_number}) {self.property}'


class MailingAddress(models.Model):
    city = models.CharField(max_length=20)
    line1 = models.CharField(max_length=50)
    line2 = models.CharField(blank=True, max_length=50, null=True)
    name = models.CharField(max_length=30, unique=True)
    state = USStateField()
    zip_code = models.CharField(max_length=10)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Mailing addresses'

    def __str__(self):
        ret = f'{self.name}: {self.line1}'
        if self.line2:
            ret += f', {self.line2}'
        ret += f', {self.city}, {self.state}, {self.zip_code}'
        return ret


class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    prefix = models.CharField(blank=True, default=None, max_length=5, null=True)
    residential_property = models.ForeignKey('Property')
    suffix = models.CharField(blank=True, default=None, max_length=10, null=True)
    phone = PhoneNumberField(blank=True, help_text='Example: 000-000-0000.', region='US')
    active = models.BooleanField(default=True)
    emails = models.ManyToManyField(Email, through='PersonEmail')

    class Meta:
        ordering = ('last_name', 'first_name')

    def add_prefix(self):
        return f'{self.prefix} ' if self.prefix else ''

    def add_suffix(self):
        if self.suffix == 'Esq':
            return f', {self.suffix}'
        else:
            return f' {self.suffix}' if self.suffix else ''

    @property
    def get_notices_email(self):
        try:
            return list(
                set(self.residential_property.notices_emails) & set(self.emails.values_list('email', flat=True))
            )[0]
        except IndexError:
            return ''

    @property
    def full_name(self):
        full_name = f'{self.prefix} ' if self.prefix else ''
        full_name += f'{self.first_name} {self.last_name}{self.add_suffix()}'

        return full_name

    @property
    def board_email(self):
        from mailing_lists.models import MailingList

        board_ml = MailingList.objects.get(mailbox__name='Board')
        # noinspection PyTypeChecker
        return (board_ml.members.all() & self.emails.all()).first()

    def __str__(self):
        return f'{self.last_name}, {self.first_name} [{self.residential_property.mailing_address(multiline=False)}]'


class PersonEmail(models.Model):
    email = models.OneToOneField(Email, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    class Meta:
        ordering = ('person', 'email')

    def __str__(self):
        return f'[{self.person.full_name}] {self.email}'


class Property(models.Model):
    comment = models.TextField(blank=True, null=True)
    house_number = models.SmallIntegerField()
    in_hh = models.BooleanField(default=True)
    outside_mailing_address = models.ForeignKey('MailingAddress', blank=True, null=True)
    property_type = models.ForeignKey('PropertyType')
    street = models.ForeignKey('Street')

    _notices_ml = None

    class Meta:
        ordering = ('street', 'house_number')
        verbose_name_plural = 'Properties'

    def get_all_active_people(self):
        return self.person_set.filter(active=True)

    def get_all_names(self):
        last_names = set([person.last_name + person.add_suffix() for person in self.get_all_active_people()])

        if len(last_names) == 1:
            # Same last name
            all_names = ' & '.join(
                [person.add_prefix() + person.first_name for person in self.get_all_active_people()]
            ) + ' ' + last_names.pop()
        else:
            # Different last names
            all_names = ' / '.join([person.full_name for person in self.get_all_active_people()])

        return all_names

    def get_notices_ml(self):
        from mailing_lists.models import MailingList

        if self._notices_ml is None:
            self._notices_ml = MailingList.objects.get(mailbox__name='Notices')

    @property
    def household_address(self):
        return self.mailing_address(include_names=True)

    def mailing_address(self, include_names=False, multiline=True):
        if multiline:
            line_end = '\n'
            pre_zip = '  '
        else:
            line_end = pre_zip = ', '

        if self.outside_mailing_address:
            if include_names:
                names = f'{self.outside_mailing_address.name} (for {self.street_address()}){line_end}'
            else:
                names = ''

            addr = f'{names}{self.outside_mailing_address.line1}{line_end}'

            if self.outside_mailing_address.line2:
                addr += f'{self.outside_mailing_address.line2}{line_end}'

            addr += (
                f'{self.outside_mailing_address.city}, {self.outside_mailing_address.state}{pre_zip}'
                f'{self.outside_mailing_address.zip_code}'
            )

            return addr
        else:
            names = (self.get_all_names() + line_end) if include_names else ''
            return f'{names}{self.street_address()}{line_end}Rochester, NY{pre_zip}14622'

    @property
    def notices_emails(self):
        self.get_notices_ml()

        emails = []
        for person in self.get_all_active_people():
            # noinspection PyTypeChecker
            email = (self._notices_ml.members.all() & person.emails.all()).first()
            if email:
                emails.append(email.email)

        return emails

    @property
    def receives_email_notices(self):
        return any(self.notices_emails)

    @property
    def receives_no_email(self):
        return sum([person.email_set.all().count() for person in self.get_all_active_people()]) == 0

    def street_address(self):
        return f'{self.house_number} {self.street}'

    def __str__(self):
        return f'{self.house_number} {self.street}'


class PropertyType(models.Model):
    property_type = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ('property_type',)

    def __str__(self):
        return self.property_type


class Street(models.Model):
    street = models.CharField(max_length=30, unique=True)

    class Meta:
        ordering = ('street',)

    def __str__(self):
        return self.street
