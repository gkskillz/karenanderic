import logging
import webapp2

from app import common
from app import static_handler


def handle_404(_, response, exception):
    logging.exception(exception)
    template = common.JINJA_ENV.get_template('404.html')
    response.out.write(template.render(common.base_context()))
    response.set_status(404)


def handle_500(_, response, exception):
    logging.exception(exception)
    template = common.JINJA_ENV.get_template('500.html')
    response.out.write(template.render(common.base_context()))
    response.set_status(500)


app = webapp2.WSGIApplication(
    [
        ('/(event|rsvp|asdf)?', static_handler.StaticHandler),
    ],
)
app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500
