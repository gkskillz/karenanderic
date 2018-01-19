import os
import jinja2

TEMPLATE_DIR = 'template'
JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), TEMPLATE_DIR)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
    trim_blocks=True,
)


def base_context(path=None):
    return {'navbar': _navbar_context(path)}


def _navbar_context(path):
    return {
        'links': [
            {'href': '/', 'label': 'Home', 'active': path == 'home'},
            {'href': '/event', 'label': 'Event', 'active': path == 'event'},
            {'href': '/rsvp', 'label': 'RSVP', 'active': path == 'rsvp'},
        ],
    }