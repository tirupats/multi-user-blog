from google.appengine.ext import db
from models.handler import Handler
#Likes model
class Likes(db.Model):
    blogId = db.StringProperty(required = True) # foreign key from Blog class
    likedBy = db.StringProperty(required = True) # foreign key from User class



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