import logging
import webapp2

from app import base_handler
from app import common
from app import static_handler


def handle_404(_, response, exception):
    logging.exception(exception)
    template = common.JINJA_ENV.get_template('404.html')
    response.out.write(template.render(base_handler.BaseHandler.base_context()))
    response.set_status(404)


def handle_500(_, response, exception):
    logging.exception(exception)
    template = common.JINJA_ENV.get_template('500.html')
    response.out.write(template.render(base_handler.BaseHandler.base_context()))
    response.set_status(500)


app = webapp2.WSGIApplication(
    [
        ('/(event|rsvp)?', static_handler.StaticHandler),
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
