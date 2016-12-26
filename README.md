# Multi User Blog Project

## Goals: ##

* Create a multiuser blog ite using Google App Engine.
* The signup, login and logout workflow is intuitive to a human user
* Editing and viewing workflow is intuitive to a human user.
* Pages render correctly.

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
* Blog: atabase model for the blog entity in the datastore
* NewPost: handles models pertaining to inputing a new blog
* Permalink: creates and handles permanent links for each blog
* Home: home page handler
* Login:  used to verify and perform login actions
* Register: perform user registration actions
* Logout: logout a user, and destroy any sessions the user may have saved
* Welcome: redirects to the home class
* Error404: handles common "page not found" errors
* DeletePost:  handles actions related to deletion of posts
* EditPost: handles functions associated with editing posts

## Features missing/ Possible additional improvements ##

* Social media registration and login
* Parallax effects on views would render it a more modern look
* Referer pages only keep track of 1 prior page and as a result can lead to circular reference when the "cancel" button is used on some pages

## General Advice ##

* Open the website, register as a new user, compose new blog, save,
* Test security features by trying to access links that are not allowed with each permission
* Test insertion, updation and deletion functionality for new blogs
