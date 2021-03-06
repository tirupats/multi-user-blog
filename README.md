# Multi User Blog Project

## How to run the Project
* On the web, go to link: https://multi-user-blog-st-154308.appspot.com/
* On the local machine, download all the files into a folder called blog.
* Then using command prompt (windows) or terminal (mac), navigate into the
* "blog" folder and run the following command
* dev_appserver.py .
* This will start a google app engine dev server in the current folder (blog)
* You will see the following on the screen:
* Starting module "default" running at: http://localhost:8080
* Open browser and navigate to the module hyperlink in the above step

## How to use/ General Advise ##
* Open the website, register as a new user, compose new blog, save.
* Test security features by trying to access links that are not allowed with each permission
* Test insertion, updation and deletion functionality for new blogs
* Comments cannot be made in the home page.  Comments can only be added on the individual blog page.  To visit an individual blog page, clike on "Read More..." button associated with a blog.  There, test comment features by adding, editing and deleting comments.  In order to ensure that the comments can be edited, ensure that JavaScript is enabled on the users machine.  Otherwise, editing comments will not be possible as this feature was built using jQuery modals. 
* Blogs cannot be liked/ unliked from the home page.  Likes can only be added/ deleted on the individual blog page.  A blog can be liked by clicking on the heart icon on the individual blog page.  
* If a blog is already liked by a user, the heart icon appears in red color.  Click on the heart again to remove the like.  A blog post which has not yet been liked appears in grey color. 

## Goals: ##

* Create a multiuser blog ite using Google App Engine.
* The signup, login and logout workflow is intuitive to a human user
* Editing and viewing workflow is intuitive to a human user.
* Pages render correctly.
* Users can add comment on other users' blog posts
* Users can like/ unlike other users blog posts

## Accounts and Security ##
* User accounts are appropriately handled.
* Account information is properly retained.
* Usernames are unique.
* Passwords are secure and appropriately used.
* User permissions are appropriate for logged out users.
* User permissions are appropriate for logged in users.
* Comment permissions are enforced.


## Class descriptions ##
* Handler:  base class which handles basic functions

* User: database model for the user entity in the datastore
* Blog: database model for the blog entity in the datastore
* Comments: database model for Comments in the datastore
* Likes:  database model for likes in the datastore 

* Welcome: redirects to the home class
* Home: home page handler
* NewPost: handles models pertaining to inputing a new blog
* Permalink: creates and handles permanent links for each blog
* EditPost: handles functions associated with editing posts
* DeletePost:  handles actions related to deletion of posts

* AddComment:  handles adding comments to blog posts
* EditComment:  handles editing existing comments made by a user on a blog post
* DeleteComment:  handles deletion of comments made by a user on a blog post
* likeBlog: handles like/ unlike functionality for the blog posts

* Login:  used to verify and perform login actions
* Register: perform user registration actions
* Logout: logout a user, and destroy any sessions the user may have saved

* Error404: handles common "page not found" errors

* 

## Features missing/ Possible additional improvements ##

* Currently, editing comments is implemented using jQuery.  However, if a user does not enable JavaScript on his/her machine, then the user cannot edit his/her comments. 
* Social media registration and login
* Parallax effects on views would render it a more modern look
* Referer pages only keep track of 1 prior page and as a result can lead to circular reference when the "cancel" button is used on some pages



