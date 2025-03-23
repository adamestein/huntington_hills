import os

from django.conf import settings

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

if getattr(settings, 'RUN_CRON_JOBS', None):
    def _log_output(filename):
        return f'>> {os.path.join(logdir, filename)} 2>&1'

    # All output (including exceptions) go to the log files
    logdir = os.path.join(settings.LOG_PATH, 'cron')
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
        # Run 'delete old aes data' at 12:00AM PST on the first and third Saturday of every month. Cron actually has
        # no way to do this, so we'll specify the days to run (which cover the 1st and 3rd Saturdays) and the
        # function will have to make sure it's a Saturday.
        ("0 16 * * *", "crontab.mailbox.process_mailboxes", _log_output('process_mailboxes.log')),
    ]
    CRONTAB_LOCK_JOBS = True
