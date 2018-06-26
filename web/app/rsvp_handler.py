import re

from google.appengine.ext import ndb

from app import base_handler
from app import common
from app import models

ALLOWED_LOCATIONS = set([str(models.CA_LOCATION)])


class RsvpHandler(base_handler.BaseHandler):
    """A handler which handles rendering the RSVP for and saving responses."""
    def get(self):
        context = self.base_context(path='rsvp')

        location = self.locations.get(models.CA_LOCATION)
        if location:
            rsvp = models.Rsvp.query_invitation_latest(
                self.invitation, models.CA_LOCATION)
            if not rsvp:
                rsvp = models.Rsvp.empty(self.invitation, location, self.guests)
            else:
                rsvp.add_empty_extras(location)
            context['ca_rsvp'] = rsvp

        template = common.JINJA_ENV.get_template('rsvp.html')
        self.response.out.write(template.render(context))

    def post(self):
        self.response.out.write('Submission closed')
        self.response.set_status(400)
