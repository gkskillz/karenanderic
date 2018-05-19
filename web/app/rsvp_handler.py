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
        location = self._location(self.request.POST.get('location'))
        if not location:
            self.response.out.write('Location not allowed')
            self.response.set_status(400)
            return

        rsvp = models.Rsvp.empty(self.invitation, location, self.guests)
        rsvp.comments = self.request.POST.get('comments')

        for i, guest_rsvp in enumerate(rsvp.adult_rsvps(), 1):
            name = self.request.POST.get('adult_%d_name' % i)
            if name != guest_rsvp.name:
                self.response.out.write('Mismatch in names')
                self.response.set_status(400)
                return

            guest_rsvp.rsvp = self._rsvp_code('adult_%d_rsvp' % i)
            if guest_rsvp.rsvp == models.YES_RSVP:
                guest_rsvp.meal_choice = self._rsvp_meal_choice(
                    'adult_%d_meal_choice' % i)
                guest_rsvp.meal_comments = self.request.POST.get(
                    'adult_%d_meal_comments' % i)

        for i, guest_rsvp in enumerate(rsvp.child_rsvps(), 1):
            name = self.request.POST.get('child_%d_name' % i)
            if name != guest_rsvp.name:
                self.response.out.write('Mismatch in names')
                self.response.set_status(400)
                return

            guest_rsvp.rsvp = self._rsvp_code('child_%d_rsvp' % i)
            if guest_rsvp.rsvp == models.YES_RSVP:
                guest_rsvp.meal_choice = self._rsvp_meal_choice(
                    'child_%d_meal_choice' % i, is_child=True)
                guest_rsvp.meal_comments = self.request.POST.get(
                    'child_%d_meal_comments' % i)

        guest_rsvp = rsvp.plus_one_rsvp()
        if guest_rsvp:
            guest_rsvp.name = self.request.POST.get('plus_one_name')
            guest_rsvp.rsvp = models.YES_RSVP
            guest_rsvp.meal_choice = self._rsvp_meal_choice(
                'plus_one_meal_choice')
            guest_rsvp.meal_comments = self.request.POST.get(
                'plus_one_meal_comments')

        for i, guest_rsvp in enumerate(rsvp.additional_child_rsvps(), 1):
            guest_rsvp.name = self.request.POST.get(
                'additional_child_%d_name' % i)
            guest_rsvp.rsvp = models.YES_RSVP
            guest_rsvp.meal_choice = self._rsvp_meal_choice(
                'additional_child_%d_meal_choice' % i, is_child=True)
            guest_rsvp.meal_comments = self.request.POST.get(
                'additional_child_%d_meal_comments' % i)

        rsvp.guest_rsvps = [r for r in rsvp.guest_rsvps if r.name]

        # Carry over previous answers
        old_rsvp = models.Rsvp.query_invitation_latest(
            self.invitation, location=location.location)
        if old_rsvp:
            rsvp.mailing_address = old_rsvp.mailing_address
            rsvp.shuttle_rsvp = old_rsvp.shuttle_rsvp

        rsvp.put()

        self.redirect('/rsvp')

    def _location(self, value):
        if value == 'ca':
            return self.locations.get(models.CA_LOCATION)
        return None

    def _rsvp_code(self, key):
        value = self.request.POST.get(key)
        if value == 'yes':
            return models.YES_RSVP
        if value == 'no':
            return models.NO_RSVP
        return None

    def _rsvp_meal_choice(self, key, is_child=False):
        value = self.request.POST.get(key)
        if not is_child:
            if value == 'meat':
                return models.MEAT_MEAL
            if value == 'fish':
                return models.FISH_MEAL
            if value == 'veggie':
                return models.VEGGIE_MEAL
            return None
        else:
            if value == 'meat':
                return models.MEAT_MEAL
            if value == 'fish':
                return models.FISH_MEAL
            if value == 'veggie':
                return models.VEGGIE_MEAL
            if value == 'child':
                return models.CHILD_MEAL
            if value == 'none':
                return models.NO_MEAL
            return None
