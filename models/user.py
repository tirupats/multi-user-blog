# user model
from google.appengine.ext import db
from models.errorHandlers import valid_pw, make_pw_hash
#from models.handler import Handler

class User(db.Model):
    '''
    User:  This class defines the database model for the user table
    '''
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid) #, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(#parent = users_key(),
            name = name,
            pw_hash = pw_hash,
            email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u
