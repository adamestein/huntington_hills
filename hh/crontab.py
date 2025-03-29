import os

from django.conf import settings

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

if getattr(settings, 'RUN_CRON_JOBS', None):
    def _log_output(filename):
        return f'>> {os.path.join(logdir, filename)} 2>&1'

    # All output (including exceptions) go to the log files
    logdir = os.path.join(os.environ['HOME'], 'hh', 'logs', 'cron')
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    # Date/time is EDT
    #
    # +--------- Minute (0-59)                    | Output Dumper: >/dev/null 2>&1
    # | +------- Hour (0-23)                      | Multiple Values Use Commas: 3,12,47
    # | | +----- Day Of Month (1-31)              | Do every X intervals: */X  -> Example: */15 * * * *  Is every 15 min
    # | | | +--- Month (1 -12)                    | Aliases: @reboot -> Run once at startup; @hourly -> 0 * * * *;
    # | | | | +- Day Of Week (0-6) (Sunday = 0)   | @daily -> 0 0 * * *; @weekly -> 0 0 * * 0; @monthly ->0 0 1 * *;
    # | | | | |                                   | @yearly -> 0 0 1 1 *;

    # Cron jobs
    CRONJOBS = [
        # Run every 15 minutes
        ("*/15 * * * *", "crontab.mailbox.process_mailboxes", _log_output('process_mailboxes.log')),
    ]
    CRONTAB_LOCK_JOBS = True
