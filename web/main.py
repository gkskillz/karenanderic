import logging
import webapp2

from app import base_handler
from app import common
from app import login_handler
from app import admin_handler
from app import rsvp_handler
from app import static_handler


def handle_404(_, response, exception):
    logging.exception(exception)
    template = common.JINJA_ENV.get_template('404.html')
    response.out.write(template.render(base_handler.base_context()))
    response.set_status(404)


def handle_500(_, response, exception):
    logging.exception(exception)
    template = common.JINJA_ENV.get_template('500.html')
    response.out.write(template.render(base_handler.base_context()))
    response.set_status(500)


app = webapp2.WSGIApplication(
    [
        # Main site paths
        ('/(event)?', static_handler.StaticHandler),
        ('/login', login_handler.LoginHandler),
        ('/logout', login_handler.LogoutHandler),
        ('/rsvp', rsvp_handler.RsvpHandler),

        # Admin paths
        ('/admin', admin_handler.AdminHandler),
        ('/admin/populate', admin_handler.PopulateHandler),
    ],
    config={
        'webapp2_extras.sessions': {
            'secret_key': common.session_key(),
            'cookie_args': {
                'max_age': 366 * 24 * 60 * 60,  # 1 Year
            },
        },
    }
)
app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500
