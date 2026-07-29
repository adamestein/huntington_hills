import pytest

from django_mailbox.models import Mailbox

from residents.models import Email, Person, PersonEmail, Property, PropertyType, Street

from mailing_lists.models import MailingList


@pytest.fixture
def street(db):
    return Street.objects.create(street='Test St')


@pytest.fixture
def property_type(db):
    return PropertyType.objects.create(property_type='SF')


@pytest.fixture
def property_obj(db, street, property_type):
    return Property.objects.create(
        house_number=100,
        street=street,
        property_type=property_type,
    )


@pytest.fixture
def mailbox_obj(db):
    return Mailbox.objects.create(name='Residents')


@pytest.fixture
def mailing_list(db, mailbox_obj):
    return MailingList.objects.create(
        email='residents@huntingtonhillsinc.org',
        mailbox=mailbox_obj,
    )


@pytest.fixture
def email1(db):
    return Email.objects.create(email='member1@example.com')


@pytest.fixture
def email2(db):
    return Email.objects.create(email='member2@example.com')


@pytest.mark.django_db
class TestMailingListBounceEmail:
    def test_bounce_email(self, mailing_list):
        assert mailing_list.bounce_email == 'residents-bounces@huntingtonhillsinc.org'


@pytest.mark.django_db
class TestMailingListOwnerEmail:
    def test_owner_email(self, mailing_list):
        assert mailing_list.owner_email == 'residents-owner@huntingtonhillsinc.org'


@pytest.mark.django_db
class TestMailingListMemberCanPost:
    def test_no_can_post_list_allows_all_members(self, mailing_list, email1):
        mailing_list.members.add(email1)
        assert mailing_list.member_can_post('member1@example.com') is True

    def test_can_post_list_member_on_list(self, mailing_list, email1):
        mailing_list.members.add(email1)
        mailing_list.can_post.add(email1)
        assert mailing_list.member_can_post('member1@example.com') is True

    def test_can_post_list_member_not_on_list(self, mailing_list, email1, email2):
        mailing_list.members.add(email1, email2)
        mailing_list.can_post.add(email1)
        assert mailing_list.member_can_post('member2@example.com') is False


@pytest.mark.django_db
class TestMailingListStr:
    def test_str_no_members_no_can_post(self, mailing_list):
        result = str(mailing_list)
        assert 'Residents' in result
        assert '0 members' in result
        assert 'all members can post' in result

    def test_str_with_members(self, mailing_list, email1):
        mailing_list.members.add(email1)
        result = str(mailing_list)
        assert '1 member' in result

    def test_str_with_can_post(self, mailing_list, email1):
        mailing_list.members.add(email1)
        mailing_list.can_post.add(email1)
        result = str(mailing_list)
        assert '1 member can post' in result

    def test_str_with_anonymous(self, mailing_list, email1):
        mailing_list.members.add(email1)
        mailing_list.allow_anonymous_posts = True
        mailing_list.save()
        result = str(mailing_list)
        assert 'anonymous posts allowed' in result


@pytest.mark.django_db
class TestMailingListStrPlural:
    def test_str_plural_members(self, mailing_list, email1, email2):
        mailing_list.members.add(email1, email2)
        result = str(mailing_list)
        assert '2 members' in result

    def test_str_plural_can_post(self, mailing_list, email1, email2):
        mailing_list.members.add(email1, email2)
        mailing_list.can_post.add(email1, email2)
        result = str(mailing_list)
        assert '2 members can post' in result


@pytest.mark.django_db
class TestMailingListNameSlug:
    def test_slug_set_on_save(self, mailbox_obj):
        ml = MailingList.objects.create(
            email='test@huntingtonhillsinc.org',
            mailbox=mailbox_obj,
        )
        assert ml.name_slug == 'residents'


@pytest.mark.django_db
class TestMailingListMember:
    def test_member_exists(self, mailing_list, email1, property_obj):
        person = Person.objects.create(
            first_name='Test',
            last_name='User',
            residential_property=property_obj,
        )
        PersonEmail.objects.create(email=email1, person=person)
        mailing_list.members.add(email1)

        result = mailing_list.member('member1@example.com')
        assert result == person

    def test_member_does_not_exist(self, mailing_list):
        result = mailing_list.member('nonexistent@example.com')
        assert result is None

    def test_email_not_in_members(self, mailing_list, email1):
        result = mailing_list.member('member1@example.com')
        assert result is None
