import csv
import os

from google.appengine.ext import ndb

from app import base_handler
from app import models

DIR = os.path.dirname(__file__)
GUEST_FILE = os.path.join(DIR, 'guest_list.csv')
LOCATION_FILE = os.path.join(DIR, 'location_list.csv')

LOCATION_MAP = {
    'ca': models.CA_LOCATION,
    'ca_tc': models.CA_TEA_LOCATION,
    'hk': models.HK_LOCATION,
    'hk_tea': models.HK_TEA_LOCATION,
}


class PopulateHandler(base_handler.BaseHandler):
    def get(self):
        invitations = {}

        ndb.delete_multi(models.Guest.query().fetch(keys_only=True))
        ndb.delete_multi(models.Location.query().fetch(keys_only=True))

        with open(GUEST_FILE) as guest_file:
            guest_reader = csv.DictReader(guest_file)
            for row in guest_reader:
                invitation_code = row.get('invitation_code')
                if not invitation_code:
                    continue
                invitation = self.invitation(invitation_code, invitations)
                guest = models.Guest(
                    parent=invitation.key,
                    first_name=row.get('first_name') or None,
                    last_name=row.get('last_name') or None,
                    email=row.get('email') or None,
                    is_child=row.get('is_child') == '1' or False,
                )
                guest.put()

        with open(LOCATION_FILE) as location_file:
            location_reader = csv.DictReader(location_file)
            for row in location_reader:
                invitation_code = row.get('invitation_code')
                if not invitation_code:
                    continue
                invitation = self.invitation(invitation_code, invitations)
                try:
                    location = models.Location(
                        parent=invitation.key,
                        location=LOCATION_MAP[row.get('location')],
                        has_plus_one=row.get('has_plus_one') == '1' or False,
                        additional_child_count=int(row.get(
                            'additional_child_count', 0)),
                    )
                    location.put()
                except (KeyError, ValueError):
                    continue

        self.redirect('/')

    @staticmethod
    def invitation(code, invitations):
        invitation = invitations.get(code)

        if not invitation:
            invitation = models.Invitation.query_code(code)

        if not invitation:
            invitation = models.Invitation(code=code)
            invitation.put()

        invitations[code] = invitation
        return invitation

    @staticmethod
    def is_restricted():
        return False
