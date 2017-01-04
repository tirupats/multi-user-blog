import hashlib
import re
import random
from string import letters

def isValidUsername(username):
        if len(username)<=2 or re.match('^[A-Za-z0-9 _]*[A-Za-z0-9][A-Za-z0-9_]*$.',username):
            return False
        else:
            return True
def usernameExists(username):
    if username == User.by_name(username):
        return True
    else:
        return False

def isBlankPassword(password):
    if password:
        return True
    else:
        return False

def isValidPassword(password, verify):
    if password and verify and (password==verify):
        return True
    else:
        return False

def isValidEmail(email):
    if email=='' or re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return True
    else:
        return False

def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if salt == None:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key( group = 'default'):
    return db.Key.from_path('users', group)