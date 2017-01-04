

import webapp2
import collections
import urllib2
from datetime import date
from models.comment import Comment, AddComment, EditComment, DeleteComment
from models.blog import Blog, NewPost, Permalink, Home, Welcome, Error404, EditPost, DeletePost
from models.like import Likes, likeBlog
from models.security import Register, Login, Logout

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