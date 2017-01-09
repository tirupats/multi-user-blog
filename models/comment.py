from models.handler import Handler
from google.appengine.ext import db
from models.VARS import LOGIN_PAGE
from models.blog import Blog
import webapp2

# Comments model
class Comment(db.Model):
    '''
    Comment: This class defines the database model for the comments section. 
    '''
    # foreign key from Blog class
    blogId = db.StringProperty(required = True) 
    # foreign key from User class
    author = db.StringProperty(required = True) 
    commentText = db.TextProperty(required = True)
    created = db.DateProperty(auto_now_add = True)

# Comments methods
class AddComment(Handler):
    '''
    AddComment: This class is used to add comments to an existing blog
    '''
    def post(self, post_id = ''):
        """
        AddComment.post(): Saves user comment to the database
        """
        
        if self.user:
            """
            Authentication: check that a user is logged in
            Authorization: No authorization necessary since any user 
            including the original poster can add a comment as long as they 
            are logged in
            """
            blogId = post_id
            blog = Blog.get_by_id(int(post_id))
            author = self.user.name
            commentText = self.request.get("commentText")
            a = Comment(blogId = blogId, author = author, 
                commentText = commentText)
            a.put()
            return self.redirect("/blog/%s" % str(post_id))

class EditComment(Handler):
    '''
    EditComment:  This class is used to edit an existing comments
    '''
    def post(self, comment_id):
        if self.user:
            # Authentication: check that a user is logged in
            updated_comment = Comment.get_by_id(int(comment_id))
            author = updated_comment.author
            blogId = updated_comment.blogId
            updated_comment.commentText = self.request.get("commentText")
            if self.user.name == updated_comment.author:
                #Authorization:  Users can only edit their own comments
                updated_comment.put()
                return self.redirect("/blog/%s" % str(blogId))
            else:
                return self.render("/blog/%s" % str(blogId), 
                generalError=True,
                generalErrorMsg="Unauthorized action")
        else:
            return self.render(LOGIN_PAGE, generalError=True, 
            generalErrorMsg="You must be logged in to perform that action")


class DeleteComment(Handler):
    '''
    DeleteComment: This class defines methods for deleting comments
    '''
    def get(self, comment_id = ''):
        if self.user:
            # Authentication: check that a user is logged in
            c = Comment.get_by_id(int(comment_id))
            blogId = c.blogId
            #check that the user logged in is the author of the comment
            if self.user.name == c.author:
                #Authentication: Users can delete their own comments
                db.delete(c)     
                return self.redirect("/blog/%s" % str(blogId))
            else:
                return self.render("/blog/%s" % str(blogId), 
                generalError=True, 
                generalErrorMsg="Unauthorized action")
        else:
            return self.render(LOGIN_PAGE,generalError=True, 
            generalErrorMsg="You must be logged in to perform that action") 