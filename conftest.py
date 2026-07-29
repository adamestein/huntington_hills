import os
from os import sep

import pytest


# Playwright runs tests in an async event loop, but pytest-django's DB
# operations are synchronous.  Django 5.2+ raises SynchronousOnlyOperation
# in async contexts unless this env var is set.
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')


def pytest_configure(config):
    config.addinivalue_line('markers', 'unit: Unit tests (no browser)')
    config.addinivalue_line('markers', 'behavior: Behavior/integration tests (Playwright)')

    from django.conf import settings
    if not hasattr(settings, 'RECAPTCHA_PRIVATE_KEY'):
        settings.RECAPTCHA_PRIVATE_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
        settings.RECAPTCHA_PUBLIC_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'


def pytest_collection_modifyitems(items):
    for item in items:
        fspath = str(item.fspath).replace(sep, '/')
        if 'tests/unit' in fspath:
            item.add_marker(pytest.mark.unit)
        elif 'tests/behavior' in fspath:
            item.add_marker(pytest.mark.behavior)
