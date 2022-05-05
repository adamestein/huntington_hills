from django.contrib.auth.mixins import UserPassesTestMixin


class IsBowHuntMixin(UserPassesTestMixin):
    def test_func(self):
        # noinspection PyUnresolvedReferences
        return self.request.user.is_staff or self.request.user.groups.filter(name='Bow Hunt').exists()


class IsStaffMixin(UserPassesTestMixin):
    def test_func(self):
        # noinspection PyUnresolvedReferences
        return self.request.user.is_staff
