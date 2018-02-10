import webapp2
from webapp2_extras import sessions

from app import models

INVITATION_CODE = 'invitation_code'
REDIRECT_PATH = 'redirect_path'


def base_context(path=None):
    def link(href, label, active_path):
        return {'href': href, 'label': label, 'active': path == active_path}

    return {
        'navbar': {
            'links': [
                link('/', 'Home', 'home'),
                link('/event', 'Event', 'event'),
                link('/photos', 'Photos', 'photos'),
                link('/registry', 'Registry', 'registry'),
                link('/rsvp', 'RSVP', 'rsvp'),
            ],
        },
    }


class BaseHandler(webapp2.RequestHandler):
    """The base handler for the app.

    This contains common elements such as the session store and functions to
    get the base context.

    All handlers should inherit from this instead of `webapp2.RequestHandler`.
    """

    def __init__(self, request, response):
        webapp2.RequestHandler.__init__(self, request, response)
        self.session_store = None
        self.invitation_code = None

    def dispatch(self):
        """Overrides the default dispatch and adds session functionality."""
        self.session_store = sessions.get_store(request=self.request)
        self.invitation_code = (
                self.session.get(INVITATION_CODE, '').lower() or None)

        if self.is_restricted() and not self.logged_in():
            self.session[REDIRECT_PATH] = self.request.path_qs
            self.redirect('/login')
            return

        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        """Returns the session information"""
        return self.session_store.get_session()

    @webapp2.cached_property
    def invitation(self):
        """Returns the invitation model if the user is logged in."""
        if self.invitation_code is None:
            return None
        return models.Invitation.query_code(self.invitation_code)

    @webapp2.cached_property
    def locations(self):
        """Returns the location models if the user is logged in."""
        if not self.logged_in():
            return []
        return models.Location.query_invitation(self.invitation)

    @webapp2.cached_property
    def guests(self):
        """Returns the guest models if the user is logged in."""
        if not self.logged_in():
            return []
        return models.Guest.query_invitation(self.invitation)

    def adult_guests(self):
        """Returns the guest models filter by not is_child."""
        return [g for g in self.guests if not g.is_child]

    def child_guests(self):
        """Returns the guest models filter by is_child."""
        return [g for g in self.guests if g.is_child]

    def base_context(self, path=None):
        """Returns the base context for things like the navigation bar."""
        context = base_context(path)
        locations = set()
        if self.logged_in():
            context['logged_in'] = self.logged_in()
            locations |= set(self.locations.keys())

        context['locations'] = locations
        context['is_ca'] = models.CA_LOCATION in locations
        context['is_ca_tea'] = models.CA_TEA_LOCATION in locations
        context['is_hk'] = models.HK_LOCATION in locations
        context['is_hk_tea'] = models.HK_TEA_LOCATION in locations

        return context

    def logged_in(self):
        """Returns if the user is logged in and has a valid invitation."""
        return self.invitation is not None

    @staticmethod
    def is_restricted():
        """Returns whether the page is restricted.

        Defaults to true, but can be overwritten by each handler. If the handler
        is restricted and the user is not logged in, they'll be redirected to
        the login page.
        """
        return True
