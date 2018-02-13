from google.appengine.ext import ndb


class Invitation(ndb.Model):
    code = ndb.StringProperty()

    @classmethod
    def query_code(cls, code):
        return cls.query(cls.code == code).get()


class Guest(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    is_child = ndb.BooleanProperty()

    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    @classmethod
    def query_invitation(cls, invitation, is_child=None):
        """Returns the list of guests ordered by name."""
        if not invitation:
            return []
        q = cls.query(ancestor=invitation.key)
        if is_child is not None:
            q = q.filter(cls.is_child == is_child)
        q = q.order(cls.first_name, cls.last_name)
        return q.fetch()


# Choices for the locations. Guests can RSVP for CA_LOCATION and HK_LOCATION,
# but the tea ceremony locations are just to show the information about the
# tea ceremony.
CA_LOCATION = 1
CA_TEA_LOCATION = 2
HK_LOCATION = 3
HK_TEA_LOCATION = 4


class Location(ndb.Model):
    location = ndb.IntegerProperty()
    has_plus_one = ndb.BooleanProperty()
    additional_child_count = ndb.IntegerProperty()

    @classmethod
    def query_invitation(cls, invitation):
        if not invitation:
            return {}
        locations = {}
        for location in cls.query(ancestor=invitation.key).fetch():
            locations[location.location] = location
        return locations


class LoginAttempt(ndb.Model):
    code = ndb.StringProperty()
    success = ndb.BooleanProperty(default=False)
    method = ndb.StringProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def query_invitation_latest(cls, invitation):
        if not invitation:
            return None
        q = cls.query(cls.code == invitation.code)
        q = q.order(-cls.timestamp)
        return q.get()


# Choices for the RSVP.
YES_RSVP = 1
NO_RSVP = 2
RSVP_CHOICES = [YES_RSVP, NO_RSVP]

# Choices for the meal.
MEAT_MEAL = 1
FISH_MEAL = 2
VEGGIE_MEAL = 3
CHILD_MEAL = 4
MEAL_CHOICES = [MEAT_MEAL, FISH_MEAL, VEGGIE_MEAL, CHILD_MEAL]


class GuestRsvp(ndb.Model):
    name = ndb.StringProperty(default='')
    is_child = ndb.BooleanProperty(default=False)
    is_extra = ndb.BooleanProperty(default=False)
    rsvp = ndb.IntegerProperty()
    meal_choice = ndb.IntegerProperty()
    meal_comments = ndb.StringProperty()

    def is_yes(self):
        return self.rsvp == YES_RSVP

    def is_no(self):
        return self.rsvp == NO_RSVP


class Rsvp(ndb.Model):
    location = ndb.IntegerProperty()
    guest_rsvps = ndb.StructuredProperty(GuestRsvp, repeated=True)
    mailing_address = ndb.StringProperty(default='')
    shuttle_rsvp = ndb.IntegerProperty()
    comments = ndb.StringProperty(default='')
    timestamp = ndb.DateTimeProperty(auto_now_add=True)

    def adult_rsvps(self):
        rsvps = []
        for rsvp in self.guest_rsvps:
            if not rsvp.is_extra and not rsvp.is_child:
                rsvps.append(rsvp)
        return rsvps

    def child_rsvps(self):
        rsvps = []
        for rsvp in self.guest_rsvps:
            if not rsvp.is_extra and rsvp.is_child:
                rsvps.append(rsvp)
        return rsvps

    def plus_one_rsvp(self):
        for rsvp in self.guest_rsvps:
            if rsvp.is_extra and not rsvp.is_child:
                return rsvp
        return None

    def additional_child_rsvps(self):
        rsvps = []
        for rsvp in self.guest_rsvps:
            if rsvp.is_extra and rsvp.is_child:
                rsvps.append(rsvp)
        return rsvps

    def add_empty_extras(self, location):
        if not self.plus_one_rsvp() and location.has_plus_one:
            self.guest_rsvps.append(GuestRsvp(
                name='',
                is_child=False,
                is_extra=True,
            ))

        additional_child_count = (
                location.additional_child_count -
                len(self.additional_child_rsvps()))
        for _ in range(additional_child_count):
            self.guest_rsvps.append(GuestRsvp(
                name='',
                is_child=True,
                is_extra=True,
            ))

    def is_shuttle_yes(self):
        return self.shuttle_rsvp == YES_RSVP

    def is_shuttle_no(self):
        return self.shuttle_rsvp == NO_RSVP

    @classmethod
    def empty(cls, invitation, location, guests):
        rsvp = cls(
            parent=invitation.key,
            location=location.location,
        )
        for guest in guests:
            rsvp.guest_rsvps.append(GuestRsvp(
                name=guest.full_name(),
                is_child=guest.is_child,
                is_extra=False,
            ))
        rsvp.add_empty_extras(location)
        return rsvp

    @classmethod
    def query_invitation_latest(cls, invitation, location=None):
        if not invitation or not location:
            return None
        q = cls.query(ancestor=invitation.key)
        q.filter(cls.location == location)
        q = q.order(-Rsvp.timestamp)
        return q.get()
