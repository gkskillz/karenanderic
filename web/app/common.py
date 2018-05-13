import os
import pytz

import jinja2


def _filename(f):
    """Return the filename relative to `common.py`."""
    return os.path.join(os.path.dirname(__file__), f)


SESSION_KEY_FILE = '../session_key.txt'
TEMPLATE_DIR = 'template'

ADMIN_LOCAL_TIMEZONE = pytz.timezone('US/Pacific')


def admin_datetime_format(value):
    if not value:
        return u'\u2014'  # emdash
    value = pytz.utc.localize(value)
    value = value.astimezone(ADMIN_LOCAL_TIMEZONE)
    return value.strftime('%Y/%m/%d %H:%M')


JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(_filename(TEMPLATE_DIR)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
    trim_blocks=True,
)
JINJA_ENV.filters['admin_datetime'] = admin_datetime_format


def session_key():
    """Returns the session key."""
    with open(_filename(SESSION_KEY_FILE), 'r') as f:
        return f.readline().strip()
