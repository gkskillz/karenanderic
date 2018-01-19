import jinja2
import webapp2

from app import common


class StaticHandler(webapp2.RequestHandler):
    def get(self, path='home'):
        if not path:
            path = 'home'
        template = common.JINJA_ENV.get_template('%s.html' % path)
        self.response.out.write(template.render(common.base_context(path=path)))
