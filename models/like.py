from google.appengine.ext import db
from models.handler import Handler
from models.blog import Blog
from models.VARS import LOGIN_PAGE
#Likes model
class Likes(db.Model):
    '''
    Likes: This class defines the database model for Likes
    '''
    # foreign key from Blog class
    blogId = db.StringProperty(required = True) 
    # foreign key from User class
    likedBy = db.StringProperty(required = True) 



# likeBlog methods

class likeBlog(Handler):
    '''
    likeBlog: This class defines the methods for liking/ unliking a blog
    '''
    def get(self, post_id = ''):
        if self.user:
            #Authotization: make sure a user is logged in
            blog = Blog.get_by_id(int(post_id))
            like = Likes.all().filter('blogId = ', post_id).filter(
                'likedBy = ', self.user.name)
            if self.user.name != blog.author and like.count() > 0:
                # Authotization: user cannot like his own blog
                # if the user has liked this article before, unlike it
                db.delete(like)
            else:
                like = Likes(blogId = post_id, likedBy = self.user.name)
                like.put()
            return self.redirect("/blog/%s" % str(post_id))
        else:
            return self.render(LOGIN_PAGE, generalError=True, 
            generalErrorMsg="You must be logged in to perform that action")