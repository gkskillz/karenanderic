import os
import jinja2


def _filename(f):
    """Return the filename relative to `common.py`."""
    return os.path.join(os.path.dirname(__file__), f)


SESSION_KEY_FILE = '../session_key.txt'
TEMPLATE_DIR = 'template'

JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(_filename(TEMPLATE_DIR)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
    trim_blocks=True,
)


def session_key():
    """Returns the session key."""
    with open(_filename(SESSION_KEY_FILE), 'r') as f:
        return f.readline().strip()
