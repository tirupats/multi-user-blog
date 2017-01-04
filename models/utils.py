import hmac
from models.VARS import secret

# global functions

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

def cookie_expires(d):
    ''' 
    cookie_expires(): 
        This function sets the cookie to expire in one year if the user uses the
        'remember me' option on the login screen.  Otherwise, cookie will expire at the end of the
        session caused by logout action or browser close action. 
    Arg1 (date): 
        The function adds one year to the date passed
    Returns:
        A date 1 year from the given date
    '''    
    remember_for = 1 # years
    try:
        return d.replace(year = d.year + remember_for)
    except ValueError:
        return d + date(d.year + years, 1, 1) - date(d.year, 1, 1)