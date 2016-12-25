import os
import webapp2
import jinja2
from google.appengine.ext import db
import collections
import hashlib
import hmac
from datetime import date
#from functools import wraps

from models.VARS import *
from models.errorHandlers import *


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

# Wrappers/ class decorators
# def login_required(f):
#     @wraps(f)
#     def wrap(*args, **kwargs):
#         if 'logged_in' in session:
#             return f(*args, **kwargs)
#         else:
#             return redirect()


# global functions

def render_str(template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

def cookie_expires(d):
    # All cookies expire 1 year from the day the "remember me" feature was used
    remember_for = 1 # years
    try:
        return d.replace(year = d.year + remember_for)
    else:
        return d + date(d.year + years, 1, 1) - date(d.year, 1, 1)

# Error Handlers


# Blog handler
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

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    #Initialize gets called every time by default
    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        self.response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, pre-check=0, post-check=0"
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

###### Blog related functions and classes


class User(db.Model):
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


class Blog(db.Model):
    title = db.StringProperty(required = True)
    blogText = db.TextProperty(required = True)
    created = db.DateProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('<img', '<img class="img-responsive" ')
        return render_str(HOME_PAGE, p=self)

class NewPost(Handler):
    def get(self):
        if self.user:
            self.render(NEWPOST_PAGE, user=self.user)
        else:
            generalError = True
            generalErrorMsg = "You must be logged in to post a blog!  Please login to continue."
            self.render(LOGIN_PAGE, generalError = generalError, generalErrorMsg = generalErrorMsg )

    def post(self):
        title = self.request.get("title")
        blogText = self.request.get("blogText")
        error = ""
        errorType = ""
        if self.user:   # if user is logged in
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
        else:
            # set cookie and store the blog title and blog text in the cookie. 
            # redirect user to the login page

            
            None # how do you only force users to only post content when they are logged in?
            # How to save user entry - allow them to enter text, then login, then retain the text entered and post it after logging in?
        if error:
            self.render(NEWPOST_PAGE, title = title, blogText = blogText,error = error, errorType = errorType)

class Permalink(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Blog',int(post_id))
        #currentBlog = db.GqlQuery("select * from Blog where __key__ = KEY('%s')" % key).get()
        currentBlog = db.get(key)
        if not currentBlog:
            self.error(404)
        else:
            self.render(SINGLEPOST_PAGE, blog = currentBlog)

class Home(Handler):
    def get(self, post_id=''):
        blogs = db.GqlQuery("select * from Blog order by last_modified desc limit 10")
        self.render(HOME_PAGE, blogs = blogs, user=self.user)


class Login(Handler):
    def get(self):
        if self.user:
            self.redirect(ERROR_PAGE)
        else:
            self.render(LOGIN_PAGE)

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        remember_me = self.request.get("remember-me")
        generalError = False
        generalErrorMsg = ""
        u = User.login(username, password)
        if u:
            # Display user dashboard
            self.login(u)
            self.redirect('/welcome')
            if remember_me == True:
                #set cookie to expire 1 year from now. 
                self.set_secure_cookie('expires', cookie_expires(date.today()))
        else:
            generalError = True
            generalErrorMsg = "Invalid username or password.  Please try again"
            self.render(LOGIN_PAGE, username = username, generalError = eneralError, generalErrorMsg = generalErrorMsg)

class Register(Handler):
    #@check_logged_in
    def get(self):
        if not self.user:
            self.render("register.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")
        self.username = username
        self.password = password
        self.verify = verify
        self.email = email
        errorList = {}
        errorList = {"username":isValidUsername(username),"password":isBlankPassword(password),"verify": isValidPassword(password, verify), "email":isValidEmail(email)}
        if False in errorList.values():
            self.render(REGISTER_PAGE, username=username, email=email, usernameError=errorList['username'], passwordBlank=errorList['password'], passwordError=errorList['verify'], emailError=errorList['email'])
        else:
            self.done()

    def done(self):
        #make sure the user doesnt exist
            u = User.by_name(self.username)
            if u:
                msg = "That user already exists"
                self.render(REGISTER_PAGE, username=self.username, usernameExists = msg)
            else:
                u = User.register(self.username, self.password, self.email)
                u.put()
                self.login(u)
                self.redirect('/welcome')

class Logout(Handler):
    def get(self):
        if self.user:
            self.logout();
            self.redirect('/signup')
        else:
            self.redirect('/error')

class Welcome(Handler):
    def get(self, *args, **vargs):
        if self.user:
            self.render(WELCOME_PAGE, username = self.user.name, user=self.user)
        else:
            self.redirect('/error')

class Error404(Handler):
    def get(self):
        self.render(ERROR_PAGE, user=self.user)
        

app = webapp2.WSGIApplication([ ('/', Home),
                                ('/blog/?', Home),
                                ('/newpost/?', NewPost),
                                ('/blog/([0-9]+)/?', Permalink),
                                ('/signup/?', Register),
                                ('/login/?', Login),
                                ('/welcome/?', Welcome),
                                ('/logout/?', Logout),
                                ('/error/?', Error404),
                                ('/.*', Error404)],
                                debug=True)