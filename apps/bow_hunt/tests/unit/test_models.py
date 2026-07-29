import pytest

from bow_hunt.models import (
    AdjacentSite, DataWarning, Deer, Hunter, Location,
    Log, LogSheet, LogSheetNonIPD, Officer, Site,
)
from residents.models import Person, Property, PropertyType, Street


@pytest.fixture
def street(db):
    return Street.objects.create(street='Main St')


@pytest.fixture
def property_type(db):
    return PropertyType.objects.create(property_type='Single Family')


@pytest.fixture
def property_obj(db, street, property_type):
    return Property.objects.create(
        house_number=100,
        street=street,
        property_type=property_type,
    )


@pytest.fixture
def person(db, property_obj):
    return Person.objects.create(
        first_name='John',
        last_name='Doe',
        residential_property=property_obj,
    )


@pytest.fixture
def hunter_first_last(db):
    return Hunter.objects.create(first_name='John', last_name='Smith')


@pytest.fixture
def hunter_first_only(db):
    return Hunter.objects.create(first_name='John', last_name='')


@pytest.fixture
def hunter_last_only(db):
    return Hunter.objects.create(first_name='', last_name='Smith')


@pytest.fixture
def officer_first_last(db):
    return Officer.objects.create(first_name='Jane', last_name='Doe')


@pytest.fixture
def officer_last_only(db):
    return Officer.objects.create(first_name='', last_name='Doe')


@pytest.fixture
def site(db):
    return Site.objects.create(number=1, street='Main St', zip_code='14622')


@pytest.fixture
def site_no_number(db):
    return Site.objects.create(street='Main St', zip_code='14622')


@pytest.fixture
def site_with_secondary(db):
    return Site.objects.create(number=1, secondary_number=2, street='Main St', zip_code='14622')


@pytest.fixture
def location(db, site):
    return Location.objects.create(
        line_item_number=1,
        label='Test Location',
        site=site,
        year=2024,
    )


@pytest.fixture
def location_override(db, site):
    return Location.objects.create(
        line_item_number=1,
        label='Override Location',
        site=site,
        year=2024,
        override_line_item_number=True,
        override_line_item_number_value=99,
    )


@pytest.fixture
def location_override_blank(db, site):
    return Location.objects.create(
        line_item_number=1,
        label='Override Blank',
        site=site,
        year=2024,
        override_line_item_number=True,
    )


@pytest.fixture
def log_sheet(db):
    from datetime import date
    from bow_hunt.models import Officer
    officer = Officer.objects.create(first_name='Test', last_name='Officer')
    return LogSheet.objects.create(
        date=date(2024, 1, 1),
        weather='Clear',
        temp='30F',
        officer=officer,
    )


@pytest.fixture
def log_sheet_non_ipd(db):
    from datetime import date
    return LogSheetNonIPD.objects.create(date=date(2024, 1, 2))


@pytest.fixture
def log(db, log_sheet, location):
    return Log.objects.create(
        log_sheet=log_sheet,
        location=location,
    )


@pytest.fixture
def log_with_hunter(db, log_sheet, location, hunter_first_last):
    return Log.objects.create(
        log_sheet=log_sheet,
        location=location,
        hunter=hunter_first_last,
    )


@pytest.mark.django_db
class TestHunterName:
    def test_first_and_last(self, hunter_first_last):
        assert hunter_first_last.name == 'John Smith'

    def test_first_only(self, hunter_first_only):
        assert hunter_first_only.name == 'John'

    def test_last_only(self, hunter_last_only):
        assert hunter_last_only.name == 'Smith'


@pytest.mark.django_db
class TestHunterStr:
    def test_first_and_last(self, hunter_first_last):
        assert str(hunter_first_last) == 'Smith, John'

    def test_first_only(self, hunter_first_only):
        assert str(hunter_first_only) == 'John'

    def test_last_only(self, hunter_last_only):
        assert str(hunter_last_only) == 'Smith'


@pytest.mark.django_db
class TestOfficerName:
    def test_first_and_last(self, officer_first_last):
        assert officer_first_last.name == 'Jane Doe'

    def test_last_only(self, officer_last_only):
        assert officer_last_only.name == 'Doe'


@pytest.mark.django_db
class TestOfficerStr:
    def test_first_and_last(self, officer_first_last):
        assert str(officer_first_last) == 'Officer Jane Doe'

    def test_last_only(self, officer_last_only):
        assert str(officer_last_only) == 'Officer Doe'


@pytest.mark.django_db
class TestSiteStr:
    def test_with_number(self, site):
        assert str(site) == '1 Main St'

    def test_with_secondary_number(self, site_with_secondary):
        assert str(site_with_secondary) == '1/2 Main St'

    def test_without_number(self, site_no_number):
        assert str(site_no_number) == 'Main St'


@pytest.mark.django_db
class TestSiteFullAddress:
    def test_full_address(self, site):
        assert site.full_address == '1 Main St, Rochester, 14622'


@pytest.mark.django_db
class TestLocationLineNumber:
    def test_without_override(self, location):
        assert location.line_number == 1

    def test_with_override(self, location_override):
        assert location_override.line_number == 99

    def test_with_override_blank(self, location_override_blank):
        assert location_override_blank.line_number == ''


@pytest.mark.django_db
class TestLocationStr:
    def test_without_override(self, location):
        assert str(location) == '[2024] 1. Test Location'

    def test_with_override(self, location_override):
        assert str(location_override) == '[2024] (1) 99. Override Location'

    def test_with_override_blank(self, location_override_blank):
        assert str(location_override_blank) == '[2024] (1) Override Blank'


@pytest.mark.django_db
class TestLogStr:
    def test_str_no_hunter_no_deer(self, log):
        result = str(log)
        assert 'no hunting occurred' in result

    def test_str_with_hunter_no_deer(self, log_with_hunter):
        result = str(log_with_hunter)
        assert 'did not shoot any deer' in result


@pytest.mark.django_db
class TestDeerAsStr:
    def test_male_deer(self, log_with_hunter):
        deer = Deer.objects.create(
            gender=Deer.GENDER_MALE,
            points=8,
            count=1,
            log=log_with_hunter,
        )
        assert deer.as_str == 'M-8'

    def test_female_deer(self, log_with_hunter):
        deer = Deer.objects.create(
            gender=Deer.GENDER_FEMALE,
            count=1,
            log=log_with_hunter,
        )
        assert deer.as_str == 'F'

    def test_male_deer_multiple(self, log_with_hunter):
        deer = Deer.objects.create(
            gender=Deer.GENDER_MALE,
            points=6,
            count=3,
            log=log_with_hunter,
        )
        assert deer.as_str == '3M-6'

    def test_no_gender(self, log_with_hunter):
        deer = Deer.objects.create(
            gender=None,
            count=1,
            log=log_with_hunter,
        )
        assert deer.as_str is None


@pytest.mark.django_db
class TestAdjacentSiteStr:
    def test_vacant(self):
        site = AdjacentSite.objects.create(acres=5.0, is_vacant=True)
        assert str(site) == 'Vacant Lot: 5.0'

    def test_hh_commons(self):
        site = AdjacentSite.objects.create(acres=10.0, is_hh_commons=True, is_vacant=False)
        assert str(site) == 'HH Commons: 10.0'

    def test_other(self):
        site = AdjacentSite.objects.create(acres=3.0, is_vacant=False)
        assert str(site) == '3.0'


@pytest.mark.django_db
class TestDataWarningStr:
    def test_str(self):
        warning = DataWarning.objects.create(
            label='Missing Data',
            description='Some data is missing',
            type=DataWarning.MISSING_WARNING,
        )
        assert str(warning) == 'Missing Data'


@pytest.mark.django_db
class TestLogSheetStr:
    def test_str(self, log_sheet):
        result = str(log_sheet)
        assert 'January 01, 2024' in result


@pytest.mark.django_db
class TestLogSheetNonIPDStr:
    def test_str(self, log_sheet_non_ipd):
        result = str(log_sheet_non_ipd)
        assert 'January 02, 2024' in result
