# Security & Permissions
from models.handler import Handler
from models.VARS import LOGIN_PAGE, REGISTER_PAGE, ERROR_PAGE
from models.errorHandlers import isValidUsername, isBlankPassword, \
        isValidPassword, isValidEmail
from models.user import User
#from models.utils import login_required

class Register(Handler):
    '''
    Register:  This class defines the methods used to register a new user
    '''
    def get(self):
        '''
        Register.get():  Returns the registration page
        '''
        if not self.user:
            self.render(REGISTER_PAGE)

    def post(self):
        '''
        Register.post():  Takes the user input, validates and saves to the 
        database
        '''
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")
        self.username = username
        self.password = password
        self.verify = verify
        self.email = email
        errorList = {}
        errorList = {"username":isValidUsername(username),
                    "password":isBlankPassword(password),
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
        '''
        register.done(): Saves new user
        '''
        #make sure the user doesnt exist
        u = User.by_name(self.username)
        if u:
            msg = "That user already exists"
            self.render(REGISTER_PAGE, username=self.username, 
                usernameExists = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()
            self.login(u)
            self.redirect('/welcome')

class Login(Handler):
    '''
    Login:  This class defines methods for the logging in existing users
    '''
    def get(self):
        '''
        Login.get():  Returns the login page
        '''
        if self.user:
            self.render(ERROR_PAGE, msg = "You are already logged in")
        else:
            self.render(LOGIN_PAGE)

    def post(self):
        '''
        Login.post():  Validates user input and logins in the user if the
        credentials provided are valid.
        '''
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
                self.set_secure_cookie('expires', 
                    cookie_expires(date.today()))
        else:
            generalError = True
            generalErrorMsg = "Invalid username or password.  "
            self.render(LOGIN_PAGE, username = username, 
            generalError = generalError, generalErrorMsg = generalErrorMsg)


class Logout(Handler):
    '''
    Logout():  This class defines methods to log a user out and destroy 
    the session
    '''
    #@login_required(Handler().self.user)
    def get(self):
        if self.user:
            self.logout();
            self.redirect('/')
        else:
            self.render(ERROR_PAGE, msg = "Unauthorized action attempt")