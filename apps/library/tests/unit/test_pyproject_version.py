import tomllib
from pathlib import Path

import pytest

from django.conf import settings


@pytest.mark.unit
def test_pyproject_version_matches():
    pyproject = tomllib.loads(
        (Path(__file__).resolve().parent.parent.parent.parent.parent / "pyproject.toml").read_text()
    )
    assert pyproject["project"]["version"] == settings.VERSION, (
        f"pyproject.toml version ({pyproject['project']['version']}) "
        f"doesn't match settings.VERSION ({settings.VERSION})"
    )
