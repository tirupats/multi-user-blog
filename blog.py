import os
import webapp2
import jinja2
from google.appengine.ext import db
import collections
import hashlib
import hmac
import urllib2
from datetime import date

from models.VARS import *
from models.errorHandlers import *

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

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
# All cookies will be set to expire in 1 year or on logout if "remember me" feature is used
    remember_for = 1 # years
    try:
        return d.replace(year = d.year + remember_for)
    except ValueError:
        return d + date(d.year + years, 1, 1) - date(d.year, 1, 1)

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
            '%s=%s; Path=/; expires=0;' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/; expires=; expiration=;')
    
    def makeImagesResponsive(self, blogText):
        # If the user posts images in the blog, make the images responsive.
        return blogText.replace('<img ', '<img class="img img-responsive" ')

    #Initialize gets called every time by default
    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        self.response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, pre-check=0, post-check=0"
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

# user model

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


# blog model
class Blog(db.Model):
    title = db.StringProperty(required = True)
    blogText = db.TextProperty(required = True)
    author = db.StringProperty(required = True) # foreign key from User class
    created = db.DateProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('<img', '<img class="img-responsive" ')
        return render_str(HOME_PAGE, p=self)

# Comments model
class Comment(db.Model):
    blogId = db.StringProperty(required = True) # foreign key from Blog class
    author = db.StringProperty(required = True) # foreign key from User class
    commentText = db.StringProperty(required = True)
    created = db.DateProperty(auto_now_add = True)

#Likes model
class Likes(db.Model):
    blogId = db.StringProperty(required = True) # foreign key from Blog class
    likedBy = db.StringProperty(required = True) # foreign key from User class

# Comments methods
class AddComment(Handler):
    def post(self, post_id = ''):
        blogId = post_id
        author = self.user.name
        commentText = self.request.get("commentText")
        if self.user:
            a = Comment(blogId = blogId, author = author, commentText = commentText)
            a.put()
        return self.redirect("/blog/%s" % str(post_id))

class EditComment(Handler):
    def post(self, comment_id):
        updated_comment = Comment.get_by_id(int(comment_id))
        blogId = updated_comment.blogId
        updated_comment.commentText = self.request.get("commentText")
        updated_comment.put()
        return self.redirect("/blog/%s" % str(blogId))


class DeleteComment(Handler):
    def get(self, comment_id = ''):
        c = Comment.get_by_id(int(comment_id))
        blogId = c.blogId
        db.delete(c)     
        return self.redirect("/blog/%s" % str(blogId)) 

# likeBlog methods

class likeBlog(Handler):
    def get(self, post_id = ''):
        like = Likes.all().filter('blogId = ', post_id).filter('likedBy = ', self.user.name)
        if like.count() > 0:
            db.delete(like)
        else:
            like = Likes(blogId = post_id, likedBy = self.user.name)
            like.put()
        return self.redirect("/blog/%s" % str(post_id))


# Blog methods
class NewPost(Handler):
# This class defines logic associated with processing new blog posts.
    def get(self):
        if self.user:
            # Keep track of prior page (or referer) to enable "cancel"" functionality
            if self.request.referrer == None:
                referer = "/blog"
            else:
                referer = self.request.referer
            self.render(NEWPOST_PAGE, user=self.user, referer = referer)
        else:
            generalError = True
            generalErrorMsg = "You must be logged in to post a blog!  Please login to continue."
            self.render(LOGIN_PAGE, generalError = generalError, generalErrorMsg = generalErrorMsg )

    def post(self):
        title = self.request.get("title")
        blogText = (self.makeImagesResponsive(self.request.get("blogText"))).rstrip();
        author = self.user.name
        error = ""
        errorType = ""
        if self.user:   # if user is logged in
            if (title and blogText):
                a = Blog(title = title, author = author, blogText = blogText)
                a.put()
                errorType = 0
                self.redirect("/blog/%s" % str(a.key().id()))
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
            # redirect user to home page
            self.redirect(HOME_PAGE)
        if error:
            self.render(NEWPOST_PAGE, title = title, blogText = blogText,error = error, errorType = errorType, 
                referer = self.request.referer)

class Permalink(Handler):
    def get(self, post_id=''):
        try:
            currentBlog = Blog.get_by_id(int(post_id))
            qry = "SELECT * FROM Comment WHERE blogId = '%s' ORDER BY created DESC" % (post_id)
            #comments = Comment.all().filter('blogId = ', post_id).order('-created')
            comments = db.GqlQuery(qry)
        except Exception as e:
            return self.render(ERROR_PAGE, msg = e.message + "Permalink")
        if currentBlog:
            if currentBlog.author == self.user.name:
                return self.render(SINGLEPOST_PAGE, blog = currentBlog, user = self.user, comments = comments, liked = None)
            else:
                #liked = Likes.all().filter('blogId = ', post_id).filter('likedBy = ', self.user.name)
                qry = "SELECT * FROM Likes WHERE blogId = '%s' AND likedBy = '%s'" % (post_id, self.user.name)
                liked = db.GqlQuery(qry)
                if liked.count() > 0:
                    return self.render(SINGLEPOST_PAGE, blog = currentBlog, user = self.user, comments = comments, liked = True)
                else:
                    return self.render(SINGLEPOST_PAGE, blog = currentBlog, user = self.user, comments = comments, liked = False)
    


class Home(Handler):
    def get(self, post_id=''):
        blogs = db.GqlQuery("select * from Blog order by last_modified desc limit 10")
        self.render(HOME_PAGE, blogs = blogs, user=self.user)

class Welcome(Handler):
    def get(self, *args, **vargs):
        if self.user:
            self.redirect('/blog')
        else:
            self.redirect('/error')

class Error404(Handler):
    def get(self):
        self.render(ERROR_PAGE, user=self.user)

class DeletePost(Handler):
    def get(self, post_id=''):
        if self.user:
            key = db.Key.from_path('Blog',int(post_id))
            blog = Blog.get_by_id(int(post_id))
            if blog and key != None:
                db.delete(key)
                self.redirect("/blog")
            else:
                return self.render(ERROR_PAGE, msg = "Blog not found")
        else:
            generalError = True
            generalErrorMsg = "You must be logged in to delete a blog!  Please login to continue."
            self.render(LOGIN_PAGE, generalError = generalError, generalErrorMsg = generalErrorMsg )

    def post(self, post_id=''):
        key = db.Key.from_path('Blog',int(post_id))
        if key != None:
            db.delete(key)
            r = requests.head(self.request.referer, allow_redirects=False)
            if r.status_code != 404 :
                self.redirect(self.request.referer)
            else:
                self.redirect(Home)
        else:
            self.render(ERROR_PAGE)

class EditPost(Handler):
    def get(self, post_id=''):
        self.blog = Blog.get_by_id(int(post_id))
        if self.request.referrer == None:
            referer = "/blog"
        else:
            referer = self.request.referer
        if self.user and self.user.name == self.blog.author:
            self.render(EDITPOST_PAGE, user = self.user, 
                        referer = referer, 
                        title = self.blog.title, 
                        blogText = self.blog.blogText, 
                        blog = self.blog)
        else:
            generalError = True
            generalErrorMsg = "You must be logged in to edit a blog!  Please login to continue."
            self.render(LOGIN_PAGE, generalError = generalError, generalErrorMsg = generalErrorMsg )
    
    def post(self, post_id=''):        
        updated_blog = Blog.get_by_id(int(post_id))
        updated_blog.title = self.request.get("title")
        updated_blog.blogText = (self.makeImagesResponsive(self.request.get("blogText"))).rstrip();
        updated_blog.author = self.user.name
        error = ""
        errorType = ""
        if self.user:   # if user is logged in
            if (updated_blog.title and updated_blog.title):
                updated_blog.put()
                errorType = 0
                self.redirect("/blog/%s" % str(post_id))
            elif (updated_blog.title):
                error = "Blog Text is a required field"
                errorType = 1 # Missing Blog Text
            elif (updated_blog.blogText):
                error = "Title is a required field"
                errorType = 2 # Missing Title
            else:
                error = "Both Title and Blog text are required fields"
                errorType = 3 # Missing both title and blog text
        else:
            # redirect user to home page.  This should not happen in the current workflow
            self.redirect(HOME_PAGE)
        if error:
            self.render(EDITPOST_PAGE, blog = updated_blog, error = error, errorType = errorType)

# Security & Permissions

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
        errorList = {"username":isValidUsername(username),"password":isBlankPassword(password),
                    "verify": isValidPassword(password, verify), 
                    "email":isValidEmail(email)}
        if False in errorList.values():
            self.render(REGISTER_PAGE, username=username, email=email, 
                        usernameError=errorList['username'], 
                        passwordBlank=errorList['password'], 
                        passwordError=errorList['verify'], 
                        emailError=errorList['email'])
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

class Login(Handler):
    def get(self):
        if self.user:
            self.render(ERROR_PAGE, msg = "You are already logged in")
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
            if remember_me == "checked":
                #set cookie to expire 1 year from now. 
                self.set_secure_cookie('expires', cookie_expires(date.today()))
        else:
            generalError = True
            generalErrorMsg = "Invalid username or password.  Please try again"
            self.render(LOGIN_PAGE, username = username, generalError = generalError, generalErrorMsg = generalErrorMsg)

class Logout(Handler):
    def get(self):
        if self.user:
            self.logout();
            self.redirect('/')
        else:
            self.render(ERROR_PAGE, msg = "You must be logged in to perform that action!")

app = webapp2.WSGIApplication([ ('/', Home),
                                ('/blog/?', Home),
                                ('/newpost/?', NewPost),
                                ('/blog/([0-9]+)/?', Permalink),
                                ('/delete/([0-9]+)/?', DeletePost),
                                ('/edit/([0-9]+)/?', EditPost),
                                ('/signup/?', Register),
                                ('/login/?', Login),
                                ('/welcome/?', Welcome),
                                ('/logout/?', Logout),
                                ('/addComment/([0-9]+)/?', AddComment),
                                ('/editComment/([0-9]+)/?', EditComment),
                                ('/deleteComment/([0-9]+)/?', DeleteComment),
                                ('/like/([0-9]+)/?', likeBlog),
                                ('/error/?', Error404),
                                ('/.*', Error404)],
                                debug=True)