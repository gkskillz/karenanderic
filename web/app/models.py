from google.appengine.ext import ndb


class Invitation(ndb.Model):
    code = ndb.StringProperty()

    @classmethod
    def query_code(cls, code):
        return cls.query(cls.code == code).get()
