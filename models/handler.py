import os
import webapp2
import jinja2

from models.utils import check_secure_val
from models.utils import make_secure_val
from models.user import User


template_dir = os.path.join(os.path.join(os.path.dirname(__file__), 
os.pardir), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
autoescape=True)

# Blog handler
class Handler(webapp2.RequestHandler):
    '''
    Handler:
        This is the main class that handles all the blog related functions. 
    '''

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
        self.response.headers.add_header(
            'Set-Cookie', 'user_id=; Path=/; expires=; expiration=;')
    
    def makeImagesResponsive(self, blogText):
        # If the user posts images in the blog, make the images responsive.
        return blogText.replace('<img ', '<img class="img img-responsive" ')

    #Initialize gets called every time by default
    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        self.response.headers["Cache-Control"] = \
        "no-cache, no-store, must-revalidate, pre-check=0, post-check=0"
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))
