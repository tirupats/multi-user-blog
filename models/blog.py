from google.appengine.ext import db
from models.handler import Handler
from models.VARS import SINGLEPOST_PAGE, ERROR_PAGE, HOME_PAGE, NEWPOST_PAGE,\
                        LOGIN_PAGE, EDITPOST_PAGE
# blog model
class Blog(db.Model):
    '''
    Blog: This class represents the blog data model. 
    Args: Google App Engine database model object
    Returns: Blog table
    '''
    title = db.StringProperty(required = True)
    blogText = db.TextProperty(required = True)
    author = db.StringProperty(required = True) # foreign key from User class
    created = db.DateProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('<img', 
                            '<img class="img-responsive" ')
        return render_str(HOME_PAGE, p=self)

# Blog methods
class NewPost(Handler):
    '''
    NewPost: This class defines logic associated with processing new blog posts.
    Args: Main Handler class from the handler.py file. 
    Returns: see docstrings for get and post methods below
    '''
    def get(self):
        '''
        NewPost.get(): get method for the NewPost class
        Args: self object
        Returns: 
            If a user is logged in, the function returns newpost page
            If a user is not logged in, the function redirects the user to the 
            login page
        '''
        if self.user:
            # Keep track of prior page (or referer) to enable "cancel" 
            # functionality
            if self.request.referrer == None:
                referer = "/blog"
            else:
                referer = self.request.referer
            self.render(NEWPOST_PAGE, user=self.user, referer=referer)
        else:
            generalError = True
            generalErrorMsg = "You must be logged in to post a blog! "
            self.render(LOGIN_PAGE, generalError=generalError, generalErrorMsg=generalErrorMsg )

    def post(self):
        '''
        NewPost.post(): post method for the NewPost class.  Does basic error 
        handling for the users inputs in the newpost page
        Args: self object
        Returns: 
            If a user is not logged in, the function returns the home page
            If a user is logged in, and there are errors in the user input, 
            the function returns the newpost page along with the user inputs
            If a user is logged in, and provides valid inputs on the newpost 
            page, the function commits the users inputs to the database
        '''   
        if self.user:   # if user is logged in
            title = self.request.get("title")
            blogText = (self.makeImagesResponsive(
                            self.request.get("blogText"))).rstrip();
            author = self.user.name
            error = ""
            errorType = ""
        
            if (title and blogText):
                a = Blog(title=title, author=author, blogText=blogText)
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
            self.render(NEWPOST_PAGE, title=title, blogText=blogText,
                error=error, errorType=errorType, 
                referer = self.request.referer)

class Permalink(Handler):
    '''
    Permalink:  This class defines the logic for creating a permalink 
    for each blog that is submitted to this site. 
    Args: Handler object
    Returns: A permalink page if no errors are encountered or a redirection 
            the login page on error
    '''
    def get(self, post_id=''):
        '''
        Permalink.get(): This method returns the permalink page for a 
        specific blog if there are no errors or returns the login page on
        error
        '''
        if self.user:
            try:
                currentBlog = Blog.get_by_id(int(post_id))
                qry = "SELECT * FROM Comment WHERE blogId = '%s' " \
                      "ORDER BY created DESC" % (post_id)
                comments = db.GqlQuery(qry)
            except Exception as e:
                return self.render(ERROR_PAGE, msg=e.message + "Permalink")
            if currentBlog:
                if currentBlog.author == self.user.name:
                    return self.render(SINGLEPOST_PAGE, blog=currentBlog, 
                                        user=self.user, comments=comments, 
                                        liked=None)
                else:
                    qry = "SELECT * FROM Likes WHERE blogId = '%s' " \
                          "AND likedBy = '%s'" % (post_id, self.user.name)
                    liked = db.GqlQuery(qry)
                    if liked.count() > 0:
                        return self.render(SINGLEPOST_PAGE, blog=currentBlog, user=self.user, comments=comments, liked=True)
                    else:
                        return self.render(SINGLEPOST_PAGE, blog=currentBlog, user=self.user, comments=comments, liked=False)
        else:
            return self.render(LOGIN_PAGE, generalError=True, 
            generalErrorMsg="You need to be logged in to perform that action")


class Home(Handler):
    '''
    Home: This class is used to handle the home page of the site
    Args: Handler object
    Returns: returns the user to the home page, which shows top 10 blogs
    '''
    def get(self, post_id=''):
        '''
        Home.get(): This method returns the home page with the top 10 blogs
        '''
        blogs = db.GqlQuery("select * from Blog " \
                    "order by last_modified desc limit 10")
        self.render(HOME_PAGE, blogs=blogs, user=self.user)

class Welcome(Handler):
    '''
    Welcome: The welcome page handles the page to be shown as soon as a user
    logs in
    '''
    def get(self, *args, **vargs):
        if self.user:
            return self.redirect('/blog')
        else:
            return self.render(LOGIN_PAGE, generalError=True, 
            generalErrorMsg="You need to be logged in to perform that action")

class Error404(Handler):
    '''
    Error404: This class is used to handle the return page when a page 
    attempted by the user is not available or inaccessible with current
    privileges
    '''
    def get(self):
        self.render(ERROR_PAGE, user=self.user)

class DeletePost(Handler):
    '''
    DeletePost: This class handles the methods associated with deletion of 
    blog posts
    Args: Handler object
    '''
    def get(self, post_id=''):
        '''
        DeletePost.get(): This method deletes the blog and redirects the 
        to the blog page. 
        '''
        #check if a user is logged in
        if self.user:
            key = db.Key.from_path('Blog',int(post_id))
            blog = Blog.get_by_id(int(post_id))
            # Check to make sure the blog exists, the user is authorized \
            # and that the user logged in is the author of the blog
            if blog and key != None and blog.author == self.user.name:
                db.delete(key)
                self.redirect("/blog")
            else:
                return self.render(ERROR_PAGE, msg="Blog not found")
        else:
            generalError = True
            generalErrorMsg = "You must be logged in to delete a blog!"
            self.render(LOGIN_PAGE, generalError=generalError, generalErrorMsg=generalErrorMsg )

    def post(self, post_id=''):
        '''
        DeletePost.post(): This method deletes the post and redirects the 
        user to the page from which the user arrived at the deletion activity
        '''
        key = db.Key.from_path('Blog',int(post_id))
        blog = Blog.get_by_id(int(post_id))
        if blog and key != None and self.user.name == blog.author:
            db.delete(key)
            r = requests.head(self.request.referer, allow_redirects=False)
            if r.status_code != 404 :
                self.redirect(self.request.referer)
            else:
                self.redirect(Home)
        else:
            self.render(ERROR_PAGE)

class EditPost(Handler):
    '''
    Editpost:  This class defines the methods required handle editing posts
    '''
    def get(self, post_id=''):
        '''
        EditPost.get(): This method returns the editable version of the page
        showing the blog the user is trying to edit
        '''
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
            generalErrorMsg = "You must be logged in to edit a blog!"
            self.render(LOGIN_PAGE, generalError=generalError, generalErrorMsg=generalErrorMsg )
    
    def post(self, post_id=''):
        '''
        EditPost.post():  This method is used to save the edits back to the 
        database
        '''        
        updated_blog = Blog.get_by_id(int(post_id))
        updated_blog.title = self.request.get("title")
        updated_blog.blogText = (self.makeImagesResponsive(
            self.request.get("blogText"))).rstrip();
        #updated_blog.author = self.user.name
        error = ""
        errorType = ""
        if self.user and self.user.name == updated_blog.author:   
        # if user is logged in and authorized to perform update action
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
            # redirect user to home page.  This should not happen in the 
            # current workflow
            self.redirect(HOME_PAGE)
        if error:
            self.render(EDITPOST_PAGE, blog=updated_blog, error=error, errorType=errorType)
