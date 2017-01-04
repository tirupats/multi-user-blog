# Security & Permissions
from models.handler import Handler
from models.VARS import LOGIN_PAGE, REGISTER_PAGE
from models.errorHandlers import isValidUsername, isBlankPassword, isValidPassword, isValidEmail
from models.user import User

class Register(Handler):
    #@check_logged_in
    def get(self):
        if not self.user:
            self.render("register.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")
        self.username = username
        self.password = password
        self.verify = verify
        self.email = email
        errorList = {}
        errorList = {"username":isValidUsername(username),"password":isBlankPassword(password),
                    "verify": isValidPassword(password, verify), 
                    "email":isValidEmail(email)}
        if False in errorList.values():
            self.render(REGISTER_PAGE, username=username, email=email, 
                        usernameError=errorList['username'], 
                        passwordBlank=errorList['password'], 
                        passwordError=errorList['verify'], 
                        emailError=errorList['email'])
        else:
            self.done()

    def done(self):
        #make sure the user doesnt exist
            u = User.by_name(self.username)
            if u:
                msg = "That user already exists"
                self.render(REGISTER_PAGE, username=self.username, usernameExists = msg)
            else:
                u = User.register(self.username, self.password, self.email)
                u.put()
                self.login(u)
                self.redirect('/welcome')

class Login(Handler):
    def get(self):
        if self.user:
            self.render(ERROR_PAGE, msg = "You are already logged in")
        else:
            self.render(LOGIN_PAGE)

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        remember_me = self.request.get("remember-me")
        generalError = False
        generalErrorMsg = ""
        u = User.login(username, password)
        if u:
            # Display user dashboard
            self.login(u)
            self.redirect('/welcome')
            if remember_me == "checked":
                #set cookie to expire 1 year from now. 
                self.set_secure_cookie('expires', cookie_expires(date.today()))
        else:
            generalError = True
            generalErrorMsg = "Invalid username or password.  Please try again"
            self.render(LOGIN_PAGE, username = username, generalError = generalError, generalErrorMsg = generalErrorMsg)

class Logout(Handler):
    def get(self):
        if self.user:
            self.logout();
            self.redirect('/')
        else:
            self.render(ERROR_PAGE, msg = "You must be logged in to perform that action!")