from app import base_handler
from app import common
from app import models


INVITATION_CODE_ERR = 'invitation_code_err'


class LoginHandler(base_handler.BaseHandler):
    """A handler which handles the login to the site.

    Logins are based on a random code, not on a username and password. This code
    is validated to make sure an entry exists, and then is saved in the session
    cookie. This code is then used to determine which parts of the website are
    visible and to manage reservations.
    """

    def get(self):
        if self.logged_in():
            self.redirect(self.session.get(base_handler.REDIRECT_PATH) or '/')
            return

        invitation_code = self.request.GET.get(base_handler.INVITATION_CODE)
        if invitation_code:
            self._submit(invitation_code, method="get")
            return

        template = common.JINJA_ENV.get_template('login.html')
        context = self.base_context()

        if INVITATION_CODE_ERR in self.session:
            context['invitation_code_err'] = self.session.pop(
                    INVITATION_CODE_ERR)
        elif self.invitation_code and not self.invitation:
            self.redirect('/logout')
            return

        self.response.out.write(template.render(context))

    def post(self):
        invitation_code = self.request.POST.get(base_handler.INVITATION_CODE)
        self._submit(invitation_code, method="post")

    def _submit(self, invitation_code, method=None):
        invitation_code = (invitation_code or '').lower()

        # Store an attempt to log in.
        attempt = models.LoginAttempt(
            code=invitation_code,
            method=method,
            success=False,
        )

        try:
            if not invitation_code:
                self.session[INVITATION_CODE_ERR] = (
                        'Please provide an invitation code')
                self.redirect('/login')
                return

            if not models.Invitation.query_code(invitation_code):
                self.session[INVITATION_CODE_ERR] = (
                        'The invitation "%s" was not found' % invitation_code)
                self.redirect('/login')
                return

            attempt.success = True
            self.session[base_handler.INVITATION_CODE] = invitation_code
            self.redirect('/login')
        finally:
            attempt.put()

    @staticmethod
    def is_restricted():
        return False


class LogoutHandler(base_handler.BaseHandler):
    """A handler which logs the user out and clears the invitation code."""
    def get(self):
        if base_handler.INVITATION_CODE in self.session:
            del self.session[base_handler.INVITATION_CODE]
        self.redirect('/')

    @staticmethod
    def is_restricted():
        return False
