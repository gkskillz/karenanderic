import cgi
import csv

from google.appengine.ext import ndb

from app import base_handler
from app import common
from app import models


class BaseAdminHandler(base_handler.BaseHandler):
    @staticmethod
    def is_restricted():
        return False


class _InvitationCache(object):
    def __init__(self):
        self.cache = {}

    def get_or_create(self, code):
        invitation = self.cache.get(code)

        if not invitation:
            invitation = models.Invitation.query_code(code)

        if not invitation:
            invitation = models.Invitation(code=code)
            invitation.put()

        self.cache[code] = invitation
        return invitation


class AdminHandler(BaseAdminHandler):
    def get(self):
        template = common.JINJA_ENV.get_template('/admin/index.html')
        self.response.out.write(template.render(self.base_context()))


LOCATION_MAP = {
    'ca': models.CA_LOCATION,
    'ca_tc': models.CA_TEA_LOCATION,
    'hk': models.HK_LOCATION,
    'hk_tea': models.HK_TEA_LOCATION,
}
GUEST_LIST_ERR = 'guest_list_err'
LOCATION_LIST_ERR = 'location_list_err'
WANT_GUEST_LIST_FIELDS = [
    'invitation_code',
    'first_name',
    'last_name',
    'email',
    'is_child',
]
WANT_LOCATION_LIST_FIELDS = [
    'invitation_code',
    'location',
    'has_plus_one',
    'additional_child_count',
]


class PopulateHandler(BaseAdminHandler):
    def get(self):
        template = common.JINJA_ENV.get_template('/admin/populate.html')
        context = self.base_context()
        if GUEST_LIST_ERR in self.session:
            context['guest_list_err'] = self.session.pop(GUEST_LIST_ERR)
        if LOCATION_LIST_ERR in self.session:
            context['location_list_err'] = self.session.pop(LOCATION_LIST_ERR)

        self.response.out.write(template.render(context))

    def post(self):
        cache = _InvitationCache()

        guest_file = self.request.POST.get('guest_list')
        location_file = self.request.POST.get('location_list')

        if guest_file == '' or not guest_file.file:
            print guest_file
            self.session[GUEST_LIST_ERR] = (
                'Please provide a guest_list.csv file')
            self.redirect('/admin/populate')
            return

        if location_file == '' or not location_file.file:
            print location_file
            self.session[LOCATION_LIST_ERR] = (
                'Please provide a location_list.csv file')
            self.redirect('/admin/populate')
            return

        guest_reader = csv.DictReader(guest_file.file)
        if guest_reader.fieldnames != WANT_GUEST_LIST_FIELDS:
            self.session[GUEST_LIST_ERR] = (
                'guest_list.csv should have the fields %s' % ', '.join(
                        WANT_GUEST_LIST_FIELDS ))
            self.redirect('/admin/populate')
            return

        location_reader = csv.DictReader(location_file.file)
        if location_reader.fieldnames != WANT_LOCATION_LIST_FIELDS:
            self.session[LOCATION_LIST_ERR] = (
                'location_list.csv should have the fields %s' % ', '.join(
                        WANT_LOCATION_LIST_FIELDS))
            self.redirect('/admin/populate')
            return

        ndb.delete_multi(models.Guest.query().fetch(keys_only=True))
        ndb.delete_multi(models.Location.query().fetch(keys_only=True))
        if self.request.POST.get('delete') == 'delete':
            ndb.delete_multi(models.Invitation.query().fetch(keys_only=True))
            ndb.delete_multi(models.Rsvp.query().fetch(keys_only=True))

        for row in guest_reader:
            invitation_code = row.get('invitation_code')
            if not invitation_code:
                continue
            invitation = cache.get_or_create(invitation_code)
            guest = models.Guest(
                parent=invitation.key,
                first_name=row.get('first_name') or None,
                last_name=row.get('last_name') or None,
                email=row.get('email') or None,
                is_child=row.get('is_child') == '1' or False,
            )
            guest.put()

        for row in location_reader:
            invitation_code = row.get('invitation_code')
            if not invitation_code:
                continue
            invitation = cache.get_or_create(invitation_code)
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

        self.redirect('/admin')
