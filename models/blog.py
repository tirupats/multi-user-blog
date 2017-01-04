from google.appengine.ext import db
from models.handler import Handler
from models.VARS import SINGLEPOST_PAGE, ERROR_PAGE, HOME_PAGE, NEWPOST_PAGE, LOGIN_PAGE, \
                        EDITPOST_PAGE
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
