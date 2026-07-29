# AGENTS.md

## Project Overview

Django 5.2 website for the Huntington Hills community (huntingtonhillsinc.org). PHP Passenger deployment via `passenger_wsgi.py`. MySQL production, SQLite tests.

## Quick Start

```bash
# Install dependencies (uv preferred)
uv sync

# Run dev server
uv run python manage.py runserver

# Run all unit tests (default)
uv run pytest

# Run all behavior tests (Playwright)
uv run pytest -m behavior

# Run all tests (both unit and behavior)
uv run pytest -m ""

# Run a single app's unit tests
uv run pytest apps/mailing_lists/

# Run a single app's behavior tests
uv run pytest apps/mailing_lists/ -m behavior

# Run a specific test file
uv run pytest apps/mailing_lists/tests/unit/test_posting.py
```

## Project Structure

```
apps/           # All Django apps (on sys.path, so import as 'appname.model')
  authentication/
  bow_hunt/     # Deer hunting management (complex forms, reports)
  contact/
  crontab/      # Mailbox processing cron job
  docs/
  gallery/
  history/
  library/      # Shared utilities, templatetags, testing helpers
  mailing_lists/ # Email list management (has tests)
  news/
  residents/
  staff/
hh/             # Django project config (settings, urls, wsgi)
pkgs/           # Local/vendored packages (see below)
public/         # Static assets (css/js/img) → collected to static/
templates/      # Global templates (app templates in apps/<app>/)
conftest.py     # pytest configuration and test settings
```

## Configuration

All config via `upsilonconf` loading `.env.json` (gitignored, not committed). Sections:
- `Settings`: DB, email, debug, secret_key, allowed_hosts
- `Recaptcha`: keys for Google reCAPTCHA
- `Mailing Lists`: SMTP credentials for Mailgun

## Testing

- **Framework**: pytest with pytest-django
- **Test DB**: SQLite at `/tmp/default.db` (auto-configured in conftest.py)
- **Migrations disabled** in tests via `library.testing.migrations.DisableMigrations`
- **Passwords**: MD5 hasher in tests (no hashing overhead)
- **Fixtures**: `apps/<app>/tests/fixtures/*.json` with paths relative to project root
- **Test structure**: Unit tests in `apps/<app>/tests/unit/`, behavior tests (Playwright) in `apps/<app>/tests/behavior/`
- Tests auto-tagged with `unit` or `behavior` markers based on directory; `unit` is the default filter
- Logging suppressed to CRITICAL during tests
- Test settings configured in `conftest.py` (applies same settings as `manage.py test`)

## Gotchas

- `apps/` is on `sys.path` — import `from residents.models import Email`, not `from apps.residents.models`
- `pkgs/` contains vendored packages including a **modified** django-dynamic-formset — do not upgrade without checking `pkgs/README`
- `.env.json` contains secrets — never commit it
- `CRONTAB_LOCK_JOBS = True` — cron jobs won't re-run if already running
- `DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'` — uses legacy int PKs, not BigAutoField
- `DATA_UPLOAD_MAX_NUMBER_FIELDS = 2000` — raised for bulk log uploads

## Shell

The global opencode config (`~/.config/opencode/opencode.jsonc`) sets `"shell": "/bin/bash"`, so all commands run under bash.

## Environment

- Python >= 3.13 required (per `pyproject.toml`)
- Database: MySQL with `STRICT_ALL_TABLES` sql_mode in production
- Email: SMTP via Mailgun (production) or file-based backend (local dev)
- Timezone: America/New_York
- License: GPL v3
