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
    def query_invitation(cls, invtitation):
        if not invtitation:
            return []
        return cls.query(ancestor=invtitation.key).fetch()


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


class Rsvp(ndb.Model):
    location = ndb.IntegerProperty()
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    rsvp = ndb.IntegerProperty()
    meal_choice = ndb.IntegerProperty()
    meal_comments = ndb.StringProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
