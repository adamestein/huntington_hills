import pytest

from residents.models import (
    Board, BoardTerm, Email, LotNumber, MailingAddress,
    Person, PersonEmail, Property, PropertyType, Street,
)


@pytest.fixture
def street(db):
    return Street.objects.create(street='Huntington Hills')


@pytest.fixture
def property_type(db):
    return PropertyType.objects.create(property_type='Single Family')


@pytest.fixture
def property_obj(db, street, property_type):
    return Property.objects.create(
        house_number=123,
        street=street,
        property_type=property_type,
    )


@pytest.fixture
def email_obj(db):
    return Email.objects.create(email='test@example.com')


@pytest.fixture
def email_obj2(db):
    return Email.objects.create(email='test2@example.com')


@pytest.fixture
def person(db, property_obj, email_obj):
    p = Person.objects.create(
        first_name='John',
        last_name='Doe',
        residential_property=property_obj,
    )
    PersonEmail.objects.create(email=email_obj, person=p)
    return p


@pytest.fixture
def person_with_prefix(db, property_obj):
    p = Person.objects.create(
        first_name='Jane',
        last_name='Smith',
        prefix='Dr.',
        residential_property=property_obj,
    )
    email = Email.objects.create(email='jane@example.com')
    PersonEmail.objects.create(email=email, person=p)
    return p


@pytest.fixture
def person_with_suffix(db, property_obj):
    p = Person.objects.create(
        first_name='Bob',
        last_name='Jones',
        suffix='Jr.',
        residential_property=property_obj,
    )
    email = Email.objects.create(email='bob@example.com')
    PersonEmail.objects.create(email=email, person=p)
    return p


@pytest.fixture
def person_with_esq_suffix(db, property_obj):
    p = Person.objects.create(
        first_name='Alice',
        last_name='Brown',
        suffix='Esq',
        residential_property=property_obj,
    )
    email = Email.objects.create(email='alice@example.com')
    PersonEmail.objects.create(email=email, person=p)
    return p


@pytest.fixture
def mailing_address(db):
    return MailingAddress.objects.create(
        name='John Doe',
        line1='123 Main St',
        city='Rochester',
        state='NY',
        zip_code='14622',
    )


@pytest.fixture
def mailing_address_with_line2(db):
    return MailingAddress.objects.create(
        name='Jane Smith',
        line1='456 Oak Ave',
        line2='Apt 2',
        city='Rochester',
        state='NY',
        zip_code='14622',
    )


@pytest.mark.django_db
class TestPersonAddPrefix:
    def test_with_prefix(self, person_with_prefix):
        assert person_with_prefix.add_prefix() == 'Dr. '

    def test_without_prefix(self, person):
        assert person.add_prefix() == ''


@pytest.mark.django_db
class TestPersonAddSuffix:
    def test_with_jr_suffix(self, person_with_suffix):
        assert person_with_suffix.add_suffix() == ' Jr.'

    def test_with_esq_suffix(self, person_with_esq_suffix):
        assert person_with_esq_suffix.add_suffix() == ', Esq'

    def test_without_suffix(self, person):
        assert person.add_suffix() == ''


@pytest.mark.django_db
class TestPersonFullName:
    def test_without_prefix_or_suffix(self, person):
        assert person.full_name == 'John Doe'

    def test_with_prefix(self, person_with_prefix):
        assert person_with_prefix.full_name == 'Dr. Jane Smith'

    def test_with_suffix(self, person_with_suffix):
        assert person_with_suffix.full_name == 'Bob Jones Jr.'

    def test_with_prefix_and_esq_suffix(self, property_obj):
        p = Person.objects.create(
            first_name='Test',
            last_name='Person',
            prefix='Mr.',
            suffix='Esq',
            residential_property=property_obj,
        )
        assert p.full_name == 'Mr. Test Person, Esq'


@pytest.mark.django_db
class TestPersonStr:
    def test_str(self, person):
        result = str(person)
        assert 'Doe, John' in result
        assert '123' in result


@pytest.mark.django_db
class TestBoardTermOfficeAbbr:
    def test_all_abbrs(self):
        assert BoardTerm.office_abbr('director_at_large_1') == 'd1'
        assert BoardTerm.office_abbr('director_at_large_2') == 'd2'
        assert BoardTerm.office_abbr('president') == 'p'
        assert BoardTerm.office_abbr('secretary') == 's'
        assert BoardTerm.office_abbr('treasurer') == 't'
        assert BoardTerm.office_abbr('vice_president') == 'vp'


@pytest.mark.django_db
class TestPropertyStreetAddress:
    def test_basic(self, property_obj):
        assert property_obj.street_address() == '123 Huntington Hills'


@pytest.mark.django_db
class TestPropertyMailingAddress:
    def test_without_names_multiline(self, property_obj):
        result = property_obj.mailing_address()
        assert '123 Huntington Hills' in result
        assert 'Rochester, NY' in result
        assert '14622' in result

    def test_without_names_singleline(self, property_obj):
        result = property_obj.mailing_address(multiline=False)
        assert '123 Huntington Hills' in result
        assert ', Rochester, NY, 14622' in result

    def test_with_names_multiline(self, person):
        result = person.residential_property.mailing_address(include_names=True)
        assert 'John Doe' in result
        assert '123 Huntington Hills' in result

    def test_with_names_singleline(self, person):
        result = person.residential_property.mailing_address(include_names=True, multiline=False)
        assert 'John Doe' in result
        assert '123 Huntington Hills' in result

    def test_with_outside_address(self, property_obj, mailing_address):
        property_obj.outside_mailing_address = mailing_address
        property_obj.save()

        result = property_obj.mailing_address()
        assert '123 Main St' in result
        assert 'Rochester' in result

    def test_with_outside_address_and_names(self, person, mailing_address):
        person.residential_property.outside_mailing_address = mailing_address
        person.residential_property.save()

        result = person.residential_property.mailing_address(include_names=True)
        assert 'John Doe' in result
        assert '123 Main St' in result

    def test_with_outside_address_line2(self, property_obj, mailing_address_with_line2):
        property_obj.outside_mailing_address = mailing_address_with_line2
        property_obj.save()

        result = property_obj.mailing_address()
        assert '456 Oak Ave' in result
        assert 'Apt 2' in result


@pytest.mark.django_db
class TestMailingAddressStr:
    def test_without_line2(self, mailing_address):
        result = str(mailing_address)
        assert 'John Doe: 123 Main St' in result
        assert 'Rochester' in result

    def test_with_line2(self, mailing_address_with_line2):
        result = str(mailing_address_with_line2)
        assert 'Jane Smith: 456 Oak Ave, Apt 2' in result


@pytest.mark.django_db
class TestLotNumberStr:
    def test_str(self, property_obj):
        lot = LotNumber.objects.create(lot_number='A1', property=property_obj)
        result = str(lot)
        assert 'A1' in result

    def test_str_blank_lot(self, property_obj):
        lot = LotNumber.objects.create(lot_number=None, property=property_obj)
        result = str(lot)
        assert 'None' in result or property_obj.__str__() in result


@pytest.mark.django_db
class TestEmailStr:
    def test_str(self, email_obj):
        assert str(email_obj) == 'test@example.com'


@pytest.mark.django_db
class TestPropertyStr:
    def test_str(self, property_obj):
        result = str(property_obj)
        assert '123' in result
        assert 'Huntington Hills' in result


@pytest.mark.django_db
class TestPropertyTypeStr:
    def test_str(self, property_type):
        assert str(property_type) == 'Single Family'


@pytest.mark.django_db
class TestStreetStr:
    def test_str(self, street):
        assert str(street) == 'Huntington Hills'
