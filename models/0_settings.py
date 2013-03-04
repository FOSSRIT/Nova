# coding: utf8
DATE_FORMAT = "%m/%d/%y %I:%M %p"
MAX_FILE_STORE = 20971520
MAX_UPLOAD_SIZE = 10485760
MAX_SIZE_ENG = "10mb"

ALLOWED_HTML_TAGS = [
    'a',
    'b',
    'blockquote',
    'br/',
    'em',
    'i',
    'li',
    'ol',
    'ul',
    'u',
    'p',
    'cite',
    'code',
    'img/',
    'table',
    'tbody',
    'tr',
    'th',
    'td',
    'hr',
    's',
    'strike',
    'sub',
    'sup',
    'div',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'span',
    'font',
    'strong',
    #Flash Movies
    'object',
    'param',
    'embed',
    'meta',
    'wbr',
    'pre',
 ] 

ALLOWED_HTML_ATTR = {
    'a': ['href', 'title', 'style'],
    'img': ['src', 'alt', 'style','width','height'],
    'blockquote': ['type', 'style'],
    'p': ['style'],
    'table': ['border', 'style'],
    'span': ['style'],
    'div': ['style'],
    'font': ['style', 'face'],
    #Flash Movies
    'object':['width','height'],
    'param':['name','value'],
    'embed':['src','type','allowscriptaccess','allowfullscreen','width','height','wmode'],
    'meta':['charset'],
 }




db = DAL('sqlite://storage.sqlite')
    
#########################################################################
## Prepare Auth
##
## Get auth defined, tables will be added later on
#########################################################################
from gluon.tools import Auth
from gluon.contrib.login_methods.ldap_auth import ldap_auth

auth = Auth(globals(),db)                      # authentication/authorization

auth.settings.create_user_groups = False
auth.messages.label_remember_me = "Stay Logged In (for 30 days)"

# RIT Ldap
auth.settings.login_methods.append(ldap_auth(server='ldap.rit.edu', base_dn='ou=people,dc=rit,dc=edu'))

## Prepare Email System
from gluon.tools import Mail
mail=Mail()
mail.settings.server = 'smtp.gmail.com:587'
mail.settings.tls = True
mail.settings.sender = 'fossrit@gmail.com'
mail.settings.login = 'fossrit:southeastwards+perceptually'

auth.settings.mailer = mail
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = False

auth.messages.verify_email = """Thanks for joining the innovation community at beta.innovation.rit.edu.

Please click the following link to activate your new account.

http://%s%s/%%(key)s

Thanks again,

The Innovation Team
Note: This is an automated email. Do Not Reply, this inbox is not monitored
""" % ( request.env.http_host, URL(r=request,c='default',f='user',args=['verify_email']) )

auth.settings.register_next = URL('user', args='login')
    
# DISABLE EXTRA FEATURES
auth.settings.actions_disabled=['profile']
