import os
import webapp2
import jinja2
from google.appengine.ext import db
import collections
import re
import random
from string import letters
import hashlib
import hmac
from functools import wraps

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

secret = "123456asdfgh"

_ERROR_MESSAGES = ""
# Naming each HTML file so its easier to reference it later
_HOME_ = "home.html"
_NEWPOST_ = "newpost.html"
_LOGIN_ = "login.html"
_REGISTER_ = "register.html"
_SINGLEPOST_ = "singlepost.html"
_WELCOME_ = "welcome.html"
_404ERROR_ = "404error.html"


def render_str(template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))
        self.loggedIn = True

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        self.loggedIn = False

    def check_logged_in(self, f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if self.user != None:
                # user is logged in
                return (_404ERROR_)
        return wrap

    #Initialize gets called every time by default
    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

def isValidUsername(username):
        if len(username)<=2:
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

def isValidPassword(password, reenter_password):
    if password and reenter_password and (password==reenter_password):
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
    if not salt:
        salt = make_salt();
    h = hashlib.sha256(name + pw + salt).hexdigest();
    return '%s %s' % (salt, h);

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key( group = 'default'):
    return db.Key.from_path('users', group)


###### Blog related functions and classes


class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
            name = name,
            pw_hash = pw_hash,
            email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


class Blog(db.Model):
    title = db.StringProperty(required = True)
    blogText = db.TextProperty(required = True)
    created = db.DateProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('<img', '<img class="img-responsive" ')
        return render_str(_HOME_, p=self)

class NewPost(Handler):
    def get(self):
        self.render(_NEWPOST_)

    def post(self):
        title = self.request.get("title")
        blogText = self.request.get("blogText")
        error = ""
        errorType = ""
        if (title and blogText):
            a = Blog(title = title, blogText = blogText)
            a.put()
            errorType = 0
            self.redirect("/blog/%s" % str(a.key().id()))
            #self.render("home.html", title = title, blogText = blogText,error = error)
        elif (title):
            error = "Blog Text is a required field"
            errorType = 1 # Missing Blog Text
        elif (blogText):
            error = "Title is a required field"
            errorType = 2 # Missing Title
        else:
            error = "Both Title and Blog text are required fields"
            errorType = 3 # Missing both title and blog text
        if error:
            self.render(_NEWPOST_, title = title, blogText = blogText,error = error, errorType = errorType)

class Permalink(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Blog',int(post_id))
        #currentBlog = db.GqlQuery("select * from Blog where __key__ = KEY('%s')" % key).get()
        currentBlog = db.get(key)
        if not currentBlog:
            self.error(404)
        else:
            self.render(_SINGLEPOST_, blog = currentBlog)

class Home(Handler):
    def get(self, post_id=''):
        blogs = db.GqlQuery("select * from Blog order by last_modified desc limit 10")
        self.render(_HOME_, blogs = blogs)


class Login(Handler):
    @check_logged_in
    def get(self):
        self.render(_LOGIN_)

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        generalError = False
        generalErrorMsg = ""
        u = User.login(username, password);
        if u:
            # Display user dashboard
            self.render(_HOME_)
        else:
            self.render(_LOGIN_, username=username, generalError=True, generalErrorMsg="Invalid username or password.  Please try again" )

class Register(Handler):
    @check_logged_in
    def get(self):
        self.render("register.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        reenter_password = self.request.get("reenter_password")
        email = self.request.get("email")
        self.username = username
        self.password = password
        self.reenter_password = reenter_password
        self.email = email
        errorList = {}
        errorList = {"username":isValidUsername(username),"password":isBlankPassword(password),"reenter_password": isValidPassword(password, reenter_password), "email":isValidEmail(email)}
        if False in errorList.values():
            self.render(_REGISTER_, username=username, email=email, usernameError=errorList['username'], passwordBlank=errorList['password'], passwordError=errorList['reenter_password'], emailError=errorList['email'])
        else:
            self.done()

    def done(self):
        #make sure the user doesnt exist
            u = User.by_name(self.username)
            if u:
                msg = "That user already exists"
                self.render(_REGISTER_, username=self.username, usernameExists = msg)
            else:
                u = User.register(self.username, self.password, self.email)
                u.put()
                self.login(u)
                self.redirect('/unit3/welcome')

class Logout(Handler):
    def get(self):
        self.logout();
        self.redirect('/')

class Welcome(Handler):
    def get(self, *args, **vargs):
        if self.user:
            self.render(_WELCOME_, username = self.user.name)
        else:
            self.redirect("blank.html")

app = webapp2.WSGIApplication([ ('/', Home),
                                ('/blog/?', Home),
                                ('/newpost/?', NewPost),
                                ('/blog/([0-9]+)/?', Permalink),
                                ('/signup/?', Register),
                                ('/login/?', Login),
                                ('/unit3/welcome/?', Welcome),
                                ('/logout/?', Logout)],
                                debug=True)