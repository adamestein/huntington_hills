from django.core.validators import MinValueValidator
from django.db import models


class Hunter(models.Model):
    first_name = models.CharField(blank=True, max_length=10)
    last_name = models.CharField(blank=True, max_length=20)

    class Meta:
        ordering = ('last_name', 'first_name')
        unique_together = ('first_name', 'last_name')

    @property
    def name(self):
        # Ordering of the first and last name is different from __str__() when both are present
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        elif self.first_name:
            return self.first_name
        else:
            return self.last_name

    def __str__(self):
        if self.first_name and self.last_name:
            return f'{self.last_name}, {self.first_name}'
        elif self.first_name:
            return self.first_name
        else:
            return self.last_name


class Location(models.Model):
    line_item_number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    address = models.CharField(max_length=50)
    year = models.PositiveSmallIntegerField(
        help_text='(to verify location is being used on the correct log sheet)', validators=[MinValueValidator(2017)]
    )

    class Meta:
        ordering = ('year', 'line_item_number')
        unique_together = ('line_item_number', 'year')

    def __str__(self):
        return f'[{self.year}] {self.line_item_number}. {self.address}'


class Log(models.Model):
    GENDER_FEMALE = 'F'
    GENDER_MALE = 'M'
    GENDER_CHOICES = ((GENDER_FEMALE, 'Female'), (GENDER_MALE, 'Male'))

    incorrect_in_ipd_log = models.BooleanField(default=False)
    missing_from_ipd_log = models.BooleanField(default=False)
    log_sheet = models.ForeignKey('LogSheet')

    location = models.ForeignKey('Location')
    hunter = models.ForeignKey('Hunter', blank=True, null=True)

    deer_count = models.PositiveSmallIntegerField(default=0)
    deer_gender = models.CharField(
        blank=True, choices=GENDER_CHOICES, help_text='(only if deer shot or killed)', max_length=1, null=True
    )
    deer_points = models.PositiveSmallIntegerField(
        blank=True, default=None, help_text='(only if deer is male)', null=True
    )
    deer_tracking = models.NullBooleanField(default=None, help_text='(set only if deer shot or killed)')

    comment = models.CharField(blank=True, max_length=200)

    class Meta:
        ordering = ('log_sheet__date', 'location__line_item_number', 'hunter__last_name', 'hunter__first_name')

    @property
    def deer_as_str(self):
        if self.deer_gender:
            return f'{self.GENDER_MALE}-{self.deer_points}' if self.deer_gender == self.GENDER_MALE \
                else self.GENDER_FEMALE
        else:
            return None

    def __str__(self):
        if self.deer_count:
            action = 'shot' if self.deer_tracking else 'killed'
            msg = (
                f'[{self.log_sheet.date}] {self.hunter.name} {action} {self.deer_count} {self.deer_as_str} '
                f'deer at {self.location.address}'
            )
        elif self.hunter:
            msg = f'[{self.log_sheet.date}] {self.hunter.name} did not shoot any deer at {self.location.address}'
        else:
            msg = f'[{self.log_sheet.date}] no hunting occurred at {self.location.address}'

        if self.incorrect_in_ipd_log:
            msg += ' (data incorrect in log)'
        elif self.missing_from_ipd_log:
            msg += ' (data missing from log)'

        return msg


class LogSheet(models.Model):
    date = models.DateField(unique=True)
    weather = models.CharField(max_length=50)
    temp = models.CharField(max_length=10)
    officer = models.ForeignKey('Officer')

    class Meta:
        ordering = ('date',)

    @property
    def deer_taken(self):
        return self.log_set.filter(deer_count__gt=0).count()

    @property
    def total_archers(self):
        return self.log_set.exclude(hunter=None).exclude(hunter__first_name='<unknown>').count()

    def __str__(self):
        return f'Log sheet for {self.date.strftime("%B %d, %Y")}'


class Officer(models.Model):
    first_name = models.CharField(blank=True, max_length=10)
    last_name = models.CharField(max_length=20)

    class Meta:
        ordering = ('last_name', 'first_name')
        unique_together = ('first_name', 'last_name')

    @property
    def name(self):
        if self.first_name:
            return f'{self.first_name} {self.last_name}'
        else:
            return f'{self.last_name}'

    def __str__(self):
        if self.first_name:
            return f'Officer {self.first_name} {self.last_name}'
        else:
            return f'Officer {self.last_name}'
