import webapp2
from webapp2_extras import sessions


class BaseHandler(webapp2.RequestHandler):
    """The base handler for the app.

    This contains common elements such as the session store and functions to
    get the base context.

    All handlers should inherit from this instead of `webapp2.RequestHandler`.
    """
    session_store = None

    def dispatch(self):
        """Overrides the default dispatch and adds session functionality."""
        self.session_store = sessions.get_store(request=self.request)

        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        """Returns the session information"""
        return self.session_store.get_session()

    @staticmethod
    def base_context(path=None):
        """Returns the base context for things like the navigation bar."""
        return {'navbar': BaseHandler._navbar_context(path)}

    @staticmethod
    def _navbar_context(path):
        return {
            'links': [
                {'href': '/', 'label': 'Home', 'active': path == 'home'},
                {'href': '/event', 'label': 'Event', 'active': path == 'event'},
                {'href': '/rsvp', 'label': 'RSVP', 'active': path == 'rsvp'},
            ],
        }