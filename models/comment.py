from models.handler import Handler
from google.appengine.ext import db
# Comments model
class Comment(db.Model):
    blogId = db.StringProperty(required = True) # foreign key from Blog class
    author = db.StringProperty(required = True) # foreign key from User class
    commentText = db.StringProperty(required = True)
    created = db.DateProperty(auto_now_add = True)

# Comments methods
class AddComment(Handler):
    def post(self, post_id = ''):
        if self.user:
            blogId = post_id
            author = self.user.name
            commentText = self.request.get("commentText")
            if self.user:
                a = Comment(blogId = blogId, author = author, commentText = commentText)
                a.put()
            return self.redirect("/blog/%s" % str(post_id))

class EditComment(Handler):
    def post(self, comment_id):
        if self.user:
            updated_comment = Comment.get_by_id(int(comment_id))
            author = updated_comment.author
            blogId = updated_comment.blogId
            updated_comment.commentText = self.request.get("commentText")
            if self.user.name == updated_comment.author:
                updated_comment.put()
            return self.redirect("/blog/%s" % str(blogId))


class DeleteComment(Handler):
    def get(self, comment_id = ''):
        if self.user:
            c = Comment.get_by_id(int(comment_id))
            blogId = c.blogId
            if self.user.name == c.author:
                db.delete(c)     
            return self.redirect("/blog/%s" % str(blogId)) 