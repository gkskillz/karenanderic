from app import base_handler
from app import common


class StaticHandler(base_handler.BaseHandler):
    """A handler which serves mostly static content from the template file.

    The paths configured in the app should match the files in the base
    template directory.
    """
    def get(self, path=None):
        if not path:
            path = 'home'
        template = common.JINJA_ENV.get_template('%s.html' % path)
        self.response.out.write(template.render(self.base_context(path=path)))
