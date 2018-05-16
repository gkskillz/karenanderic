import csv

from google.appengine.api import mail
from google.appengine.ext import ndb

from app import base_handler
from app import common
from app import models


STATUS_MESSAGE = 'admin_status_message'


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


SENDER_EMAIL = 'Karen and Eric <karenandericrowe@gmail.com>'
PLAIN_TEXT_MESSAGE = '''Save the Date!

Karen Chiu and Eric Rowe are getting married!

Saturday, August 4th, 2018 at Trentadue Winery in Geyserville, CA.

Please visit out website at https://karenanderic.com and enter {code} to confirm
attendance and provide your mailing address.

Formal invitation to follow.

{personalized_url}
'''
PERSONALIZED_URL = 'https://karenanderic.com/login?invitation_code={}'


class EmailHandler(BaseAdminHandler):
    def get(self):
        template = common.JINJA_ENV.get_template('/admin/email.html')
        context = self.base_context()
        if STATUS_MESSAGE in self.session:
            context['status_message'] = self.session.pop(STATUS_MESSAGE)
        self.response.out.write(template.render(context))

    def post(self):
        lines = self.request.POST.get('invitation_codes') or ''
        codes = set()
        for line in lines.split('\n'):
            for token in line.split(','):
                token = token.strip()
                if token:
                    codes.add(token)

        status_message = []

        for code in codes:
            invitation = models.Invitation.query_code(code)
            if not invitation:
                status_message.append('Invitation "{}" not found'.format(code))
                continue
            guests = models.Guest.query_invitation(invitation, is_child=False)
            if not guests:
                status_message.append(
                    'Invitation "{}" has no guests'.format(code))
                continue

            emails = [
                g.email for g in guests
                if g.email and mail.is_email_valid(g.email)]
            if not emails:
                status_message.append(
                    'Invitation "{}" has no emails'.format(code))
                continue

            message = mail.EmailMessage(
                sender=SENDER_EMAIL,
                cc=SENDER_EMAIL,
                to=', '.join(emails),
                subject='Save the date for Karen and Eric\'s wedding!',
            )
            message.body = PLAIN_TEXT_MESSAGE.format(
                code=code,
                personalized_url=PERSONALIZED_URL.format(code),
            )
            template = common.JINJA_ENV.get_template('/email/email.html')
            message.html = template.render({
                'code': code,
                'personalized_url': PERSONALIZED_URL.format(code),
            })
            message.send()
            status_message.append(
                'Invitation "{}" sent to {}'.format(code, ', '.join(emails)))

        self.session[STATUS_MESSAGE] = '\n'.join(status_message)
        self.redirect('/admin/email')


LOCATION_MAP = {
    'ca': models.CA_LOCATION,
    'ca_tc': models.CA_TEA_LOCATION,
    'hk': models.HK_LOCATION,
    'hk_tea': models.HK_TEA_LOCATION,
}
GUEST_LIST_ERR = 'guest_list_err'
LOCATION_LIST_ERR = 'location_list_err'
WANT_GUEST_LIST_FIELDS = set([
    'invitation_code',
    'first_name',
    'last_name',
    'email',
    'is_child',
])
WANT_LOCATION_LIST_FIELDS = set([
    'invitation_code',
    'location',
    'has_plus_one',
    'additional_child_count',
])


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
            self.session[GUEST_LIST_ERR] = (
                'Please provide a guest_list.csv file')
            self.redirect('/admin/populate')
            return

        if location_file == '' or not location_file.file:
            self.session[LOCATION_LIST_ERR] = (
                'Please provide a location_list.csv file')
            self.redirect('/admin/populate')
            return

        guest_reader = csv.DictReader(guest_file.file)
        got_guest_fields = set(guest_reader.fieldnames)
        if not WANT_GUEST_LIST_FIELDS.issubset(got_guest_fields):
            self.session[GUEST_LIST_ERR] = (
                'guest_list.csv should have the fields %s' % ', '.join(
                        WANT_GUEST_LIST_FIELDS ))
            self.redirect('/admin/populate')
            return

        location_reader = csv.DictReader(location_file.file)
        got_location_fields = set(location_reader.fieldnames)
        if not WANT_LOCATION_LIST_FIELDS.issubset(got_location_fields):
            self.session[LOCATION_LIST_ERR] = (
                'location_list.csv should have the fields %s' % ', '.join(
                        WANT_LOCATION_LIST_FIELDS))
            self.redirect('/admin/populate')
            return

        ndb.delete_multi(models.Guest.query().fetch(keys_only=True))
        ndb.delete_multi(models.Location.query().fetch(keys_only=True))

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


class ResponsesHandler(BaseAdminHandler):
    def get(self):
        ca_rows = []
        q = models.Invitation.query().order(models.Invitation.code)
        for invitation in q.fetch():
            guests = models.Guest.query_invitation(invitation, is_child=False)
            login = models.LoginAttempt.query_invitation_latest(invitation)
            rsvp = models.Rsvp.query_invitation_latest(
                    invitation, location=models.CA_LOCATION)
            self._add_row(ca_rows, invitation, guests, login, rsvp)

        template = common.JINJA_ENV.get_template('/admin/responses.html')
        context = self.base_context()
        context['ca_rows'] = ca_rows
        self.response.out.write(template.render(context))

    @staticmethod
    def _add_row(rows, invitation, guests, login, rsvp):
        row = {
            'code': invitation.code,
            'names': ', '.join(g.full_name() for g in guests),
            'login_timestamp': login and login.timestamp,
        }
        if rsvp:
            row['rsvp_timestamp'] = rsvp.timestamp
            row['yes_list'] = [g.name for g in rsvp.guest_rsvps if g.is_yes()]
            row['no_list'] = [g.name for g in rsvp.guest_rsvps if g.is_no()]
        rows.append(row)


class ResponsesCsvHandler(BaseAdminHandler):
    def get(self):
        rows = []
        q = models.Invitation.query().order(models.Invitation.code)
        for invitation in q.fetch():
            rsvp = models.Rsvp.query_invitation_latest(
                    invitation, location=models.CA_LOCATION)
            if rsvp:
                login = models.LoginAttempt.query_invitation_latest(invitation)
                for guest_rsvp in rsvp.guest_rsvps:
                    row = {
                        'code': invitation.code,
                        'name': guest_rsvp.name,
                        'login_timestamp': login and str(login.timestamp),
                        'rsvp_timestamp': str(rsvp.timestamp),
                        'rsvp': models.rsvp_to_string(guest_rsvp.rsvp),
                        'is_child': models.bool_to_string(guest_rsvp.is_child),
                        'is_extra': models.bool_to_string(guest_rsvp.is_extra),
                        'meal_choice': models.meal_choice_to_string(
                            guest_rsvp.meal_choice),
                        'meal_comments': guest_rsvp.meal_comments,
                        'shuttle_rsvp': models.rsvp_to_string(
                            rsvp.shuttle_rsvp),
                        'comments': rsvp.comments,
                    }
                    row = {
                        k: v and v.encode('utf-8') for k, v in row.iteritems()
                    }
                    rows.append(row)

        self.response.headers['Content-Type'] = 'application/csv'
        fieldnames = [
            'code',
            'name',
            'login_timestamp',
            'rsvp_timestamp',
            'rsvp',
            'is_child',
            'is_extra',
            'meal_choice',
            'meal_comments',
            'shuttle_rsvp',
            'comments',
        ]
        writer = csv.DictWriter(self.response.out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
