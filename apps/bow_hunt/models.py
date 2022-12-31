from django.core.validators import MinValueValidator
from django.db import models


class AdjacentSite(models.Model):
    acres = models.FloatField()
    adjacent_sites = models.ManyToManyField('self', blank=True, symmetrical=False)
    is_durand_eastman_golf_course = models.BooleanField(default=False)
    is_durand_eastman_park = models.BooleanField(default=False)
    is_hh_commons = models.BooleanField(default=False)
    is_irondequoit_bay_park_west = models.BooleanField(default=False)
    is_irondequoit_town_land = models.BooleanField(default=False)
    is_vacant = models.BooleanField(default=True)

    def __str__(self):
        if self.is_hh_commons:
            prefix = 'HH Commons'
        elif self.is_vacant:
            prefix = 'Vacant Lot'
        else:
            prefix = ''

        if prefix:
            prefix += ': '

        return f'{prefix}{self.acres}'


class DataWarning(models.Model):
    INCORRECT_WARNING = 0
    MISSING_WARNING = 1

    warning_choices = (
        (INCORRECT_WARNING, 'Incorrect'),
        (MISSING_WARNING, 'Missing')
    )

    label = models.CharField(max_length=70)
    description = models.CharField(blank=True, max_length=200)
    type = models.PositiveSmallIntegerField(choices=warning_choices)

    class Meta:
        ordering = ('type', 'label')

    def __str__(self):
        return self.label


class Deer(models.Model):
    GENDER_FEMALE = 'F'
    GENDER_MALE = 'M'
    GENDER_CHOICES = ((GENDER_FEMALE, 'Female (Doe)'), (GENDER_MALE, 'Male (Buck)'))

    count = models.PositiveSmallIntegerField(default=0)
    gender = models.CharField(
        blank=True, choices=GENDER_CHOICES, max_length=1, null=True
    )
    log = models.ForeignKey('Log')
    points = models.PositiveSmallIntegerField(
        blank=True, default=None, help_text='(set only if deer is male, set to 0 if unknown)', null=True
    )
    tracking = models.BooleanField(default=False)

    class Meta:
        ordering = ('log',)
        verbose_name_plural = 'Deer'

    @property
    def as_str(self):
        if self.gender:
            msg = f'{self.count}' if self.count > 1 else ''
            msg += f'{self.GENDER_MALE}-{self.points}' if self.gender == self.GENDER_MALE \
                else self.GENDER_FEMALE
            return msg
        else:
            return None

    def __str__(self):
        action = 'shot' if self.tracking else 'killed'
        cause = self.log.hunter if self.log.hunter else self.log.nonhunter.description

        msg = f'[{self.log.log_sheet.date}/{cause}] {action} {self.as_str}'
        msg += f' at {self.log.location.label}'
        return msg


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
    label = models.CharField(max_length=50)
    site = models.ForeignKey('Site', blank=True, default=None, null=True)
    year = models.PositiveSmallIntegerField(
        help_text='(to verify location is being used on the correct log sheet)', validators=[MinValueValidator(2017)]
    )

    # Because the log sheets sometimes have locations added to the end of the regular sheet (sometimes with line
    # numbers, sometimes without), we need a way to override what is displayed. If override_line_item_number is True,
    # then the value in override_line_item_number_value is displayed instead of line_item_number. line_item_number still
    # needs to have a value to determine where this location is in the order (since the override value can be blank).
    override_line_item_number = models.BooleanField(default=False)
    override_line_item_number_value = models.PositiveSmallIntegerField(
        blank=True, validators=[MinValueValidator(1)], null=True
    )

    class Meta:
        ordering = ('year', 'line_item_number')
        unique_together = ('label', 'line_item_number', 'year')

    @property
    def line_number(self):
        if self.override_line_item_number:
            return self.override_line_item_number_value if self.override_line_item_number_value else ''
        else:
            return self.line_item_number

    def __str__(self):
        if self.override_line_item_number:
            number = f'({self.line_item_number})'
            if self.override_line_item_number_value:
                number += f' {self.override_line_item_number_value}.'
        else:
            number = f'{self.line_item_number}.'
        return f'[{self.year}] {number} {self.label}'


class Log(models.Model):
    log_sheet = models.ForeignKey('LogSheet')

    location = models.ForeignKey('Location')
    hunter = models.ForeignKey('Hunter', blank=True, null=True)

    comment = models.CharField(blank=True, max_length=200)

    incorrect_warnings = models.ManyToManyField(
        DataWarning, blank=True, limit_choices_to={'type': DataWarning.INCORRECT_WARNING},
        related_name='incorrect_warnings'
    )
    missing_warnings = models.ManyToManyField(
        DataWarning, blank=True, limit_choices_to={'type': DataWarning.MISSING_WARNING},
        related_name='missing_warnings'
    )

    class Meta:
        ordering = ('log_sheet__date', 'location__line_item_number', 'hunter__last_name', 'hunter__first_name')
        unique_together = ('log_sheet', 'location', 'hunter')

    def __str__(self):
        if self.deer_set.all():
            if self.hunter:
                msg = f'[{self.log_sheet.date}] {self.hunter.name} shot deer at {self.location.label}'
            else:
                msg = (
                    f'[{self.log_sheet.date}] deer killed at {self.location.label} due to '
                    f'{self.nonhunter.description}'
                )
        elif self.hunter:
            msg = f'[{self.log_sheet.date}] {self.hunter.name} did not shoot any deer at {self.location.label}'
        else:
            msg = f'[{self.log_sheet.date}] no hunting occurred at {self.location.label}'

        if self.incorrect_warnings.all().exists():
            msg += ' (data incorrect in log)'
        elif self.missing_warnings.all().exists():
            msg += ' (data missing from log)'

        return msg


class LogSheet(models.Model):
    date = models.DateField(unique=True)
    weather = models.CharField(max_length=50)
    temp = models.CharField(max_length=10)
    comment = models.CharField(blank=True, max_length=200)
    officer = models.ForeignKey('Officer')

    class Meta:
        ordering = ('date',)

    @property
    def deer_taken(self):
        return sum([sum([deer.count for deer in log.deer_set.all()]) for log in self.log_set.all()])

    @property
    def total_archers(self):
        return self.log_set.exclude(hunter=None)\
            .exclude(hunter__first_name='<unknown>')\
            .exclude(incorrect_warnings__label='Listed hunter didn\'t actually hunt here') \
            .distinct()\
            .values('hunter')\
            .count()

    def __str__(self):
        return f'Log sheet for {self.date.strftime("%B %d, %Y")}'


class NonHunter(models.Model):
    description = models.CharField(max_length=50)
    log = models.OneToOneField(Log)

    def __str__(self):
        return f'[{self.log.log_sheet.date}] Deer killed due to {self.description}'


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


class Site(models.Model):
    # Fields are in order they should appear in the Django Admin form
    number = models.PositiveIntegerField(blank=True, null=True)
    secondary_number = models.PositiveIntegerField(blank=True, default=None, null=True)
    street = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    acres = models.FloatField(blank=True, default=None, null=True)
    town_owned = models.BooleanField(default=False)
    comment = models.CharField(blank=True, max_length=200)
    adjacent_sites = models.ManyToManyField(AdjacentSite, blank=True)

    class Meta:
        ordering = ('number', 'street')
        unique_together = ('number', 'street', 'zip_code')

    @property
    def adjacent_site_list(self):
        adj_list = []

        self._adjacent_site_list(self.adjacent_sites.all(), adj_list, 0)

        return adj_list

    def _adjacent_site_list(self, sites, adj_list, depth):
        for adj_site in sites:
            if adj_site.is_durand_eastman_golf_course:
                land_type = 'Durand Eastman Golf Course'
            elif adj_site.is_durand_eastman_park:
                land_type = 'Durand Eastman Park'
            elif adj_site.is_hh_commons:
                land_type = 'HH Commons'
            elif adj_site.is_irondequoit_bay_park_west:
                land_type = 'Irondequoit Bay Park West'
            elif adj_site.is_irondequoit_town_land:
                land_type = 'Irondequoit town'
            elif adj_site.is_vacant:
                land_type = 'vacant'
            else:
                raise RuntimeError(f'Unknown land type for {adj_site}')

            if depth:
                adj_list[-1] += f', which in turn, is adjacent to {adj_site.acres} acres of {land_type} land'
            else:
                adj_list.append(f'This property is adjacent to {adj_site.acres} acres of {land_type} land')

            if adj_site.adjacent_sites.count():
                self._adjacent_site_list(adj_site.adjacent_sites.all(), adj_list, depth + 1)
            else:
                adj_list[-1] += '.'

    @property
    def full_address(self):
        return str(self) + f', Rochester, {self.zip_code}'

    @property
    def location_aliases(self):
        return self.location_set.values_list('label', flat=True).distinct().order_by('label')

    def __str__(self):
        number = f'{self.number}/{self.secondary_number}' if self.secondary_number else self.number
        street = self.street if self.street else 'n/a'
        return f'{number} {street}' if self.number else street
