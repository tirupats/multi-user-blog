import hashlib
import re
import random
from string import letters

def isValidUsername(username):
    '''
    isValidUsername: Checks if a username is valid_pw
    '''
    if len(username)<=2 or \
    re.match('^[A-Za-z0-9 _]*[A-Za-z0-9][A-Za-z0-9_]*$.',username):
        return False
    else:
        return True
def usernameExists(username):
    '''
    usernameExists: Checks if a user already exists in the database
    '''
    return True if username == User.by_name(username) else False

def isBlankPassword(password):
    '''
    isBlankPassword: Checks if the password field is blank
    '''
    return bool(password)

def isValidPassword(password, verify):
    '''
    isValidPassword: Checks if a password is valid
    '''
    if password and verify and (password==verify):
        return True
    else:
        return False

def isValidEmail(email):
    '''
    isValidEmail: Checks if the provided email address is valid
    '''
    if email=='' or re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return True
    else:
        return False

def make_salt(length = 5):
    '''
    make_salt:  Creates a random string to be used as a salt
    '''
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    '''
    make_pw_hash: Hashes the password 
    '''
    if salt == None:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    '''
    valid_pw: checks if a password is valid against the hashlib
    '''
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key( group = 'default'):
    '''
    users_key:  Sets up default user group
    '''
    return db.Key.from_path('users', group)