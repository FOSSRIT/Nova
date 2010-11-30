# -*- coding: utf-8 -*- 

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('gae')                           # connect to Google BigTable
    session.connect(request, response, db = db) # and store sessions and tickets there
else:                                         # else use a normal relational database
    db = DAL('sqlite://storage.sqlite')       # if not, use SQLite or other DB

#########################################################################
## Prepare Auth
##
## Get auth defined, tables will be added later on
#########################################################################
from gluon.tools import Auth
from gluon.contrib.login_methods.ldap_auth import ldap_auth

auth = Auth(globals(),db)                      # authentication/authorization

auth.messages.label_remember_me = "Stay Logged In (for 30 days)"

# RIT Ldap
auth.settings.login_methods.append(ldap_auth(server='ldap.rit.edu', base_dn='ou=people,dc=rit,dc=edu'))

## Prepare Email System
from gluon.tools import Mail
mail=Mail()
mail.settings.server = 'smtp.gmail.com:587'
mail.settings.tls = True
mail.settings.sender = 'fossrit@gmail.com'
mail.settings.login = 'fossrit:1CvTS3sIwT4hNz9Fh805TIDCc'

auth.settings.mailer = mail
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = False

auth.messages.verify_email = """Thanks for joining the innovation community at beta.innovation.rit.edu.

Please click the following link to activate your new account.

http://%s%s/%%(key)s

Thanks again,

The Innovation Team
""" % ( request.env.http_host, URL(r=request,c='default',f='user',args=['verify_email']) )

auth.settings.register_next = URL('user', args='login')
    
# DISABLE EXTRA FEATURES
auth.settings.actions_disabled=['profile']

def log_to_string(entry, links=True):
    user = db(db.auth_user.id==entry.user).select(db.auth_user.home_node).first()
    home_node = db(db.node.id==user.home_node).select().first()
    
    def link_page(entry):
        page = db(db.node.id==entry.target).select().first()
        page2 = db(db.node.id==entry.target2).select().first()
        
        if page and page2:
            return "linked <a href=\"%s\">%s</a> to <a href=\"%s\">%s</a>." % (
                    URL('main','node',args=page.url),
                    page.name,
                    URL('main','node',args=page2.url),
                    page2.name
                )
        else:
            if page2:
               page = page2
               
            return "linked <a href=\"%s\">%s</a> to a page that no longer exists." % (
                    URL('main','node',args=page.url),
                    page.name
                )
    
    def unlink_page(entry):
        page = db(db.node.id==entry.target).select().first()
        page2 = db(db.node.id==entry.target2).select().first()
        
        if page and page2:
        
            return "unlinked <a href=\"%s\">%s</a> from <a href=\"%s\">%s</a>." % (
                    URL('main','node',args=page.url),
                    page.name,
                    URL('main','node',args=page2.url),
                    page2.name
                )
        else:
            if page2:
               page = page2
               
            return "unlinked <a href=\"%s\">%s</a> from a page that no longer exists." % (
                    URL('main','node',args=page.url),
                    page.name
                )
    
    def add_page(entry):
        page = db(db.node.id==entry.target).select().first()
        
        if page:
            return "created a new page entitled <a href=\"%s\">%s</a>." % (URL('main','node',args=page.url), page.name)
        else:
            return "created a new page that no longer exists"
            
    def edit_page(entry):
        page = db(db.node.id==entry.target).select().first()
    
        if page:
            return "edited <a href=\"%s\">%s</a>'s %s" % (
                URL('main','node',args=page.url),
                page.name,
                entry.target2
            )
        else:
            return "edited a page that no longer exists"
            
    def delete_page(entry):
        return "deleted a page"
        
    def add_attribute(entry):
        page = db(db.node.id==entry.target).select().first()
        
        if page:
            attribute = db(db.nodeAttr.id==entry.target2).select().first()
            if attribute:
                return "Added %s attribute to <a href=\"%s\">%s</a>." % (
                        attribute.vocab.value,
                        URL('main','node',args=page.url),
                        page.name
                    )
            else:
                return "Added an attribute that no longer exists to <a href=\"%s\">%s</a>." % (
                        URL('main','node',args=page.url),
                        page.name
                    )
        else:
            return "Added an attribute to a page that no longer exists."
    
        
    def edit_attribute(entry):
        page = db(db.node.id==entry.target).select().first()
        
        if page:
            attribute = db(db.nodeAttr.id==entry.target2).select().first()
            if attribute:
                return "Edited %s attribute of <a href=\"%s\">%s</a>." % (
                        attribute.vocab.value,
                        URL('main','node',args=page.url),
                        page.name
                    )
            else:
                return "Edited an attribute that no longer exists of <a href=\"%s\">%s</a>." % (
                        URL('main','node',args=page.url),
                        page.name
                    )
        else:
            return "Edited an attribute to a page that no longer exists."
    
    def del_attriubte(entry):
        page = db(db.node.id==entry.target).select().first()
        
        if page:
            attribute = db(db.nodeAttr.id==entry.target2).select().first()
            return "Deleted an attribute from <a href=\"%s\">%s</a>." % (
                        URL('main','node',args=page.url),
                        page.name
                    )
        else:
            return "Deleted an attribute from a page that no longer exists."

    switch = {
        "Linked Page":link_page,
        "Unlinked Page":unlink_page,
        "Added Page":add_page,
        "Edited Page":edit_page,
        "Deleted Page":delete_page,
        "Added Attribute":add_attribute,
        "Edited Attribute":edit_attribute,
        "Deleted Attribute":del_attriubte
        }
    
    ret_val = "%s | <a href=\"%s\">%s</a> %s" % (
            entry.date.strftime("%d/%m/%y %I:%M %p"),
            URL('main','node',args=home_node.url),
            home_node.name,
            switch[entry.action](entry)
        )
        
    if links:
        return ret_val
    else:
        return TAG(ret_val).flatten()
        
def log_str_auto_compute(record):
    if not record.has_key('user'):
        record['user'] = auth.user_id
    if not record.has_key('date'):
        record['date'] = request.now
    class DictObj(dict):
        def __getattr__(self, name):
            try:
                return self.__getitem__(name)
            except KeyError:
                return super(DictObj,self).__getattr__(name)

    msg = log_to_string(DictObj(record))

    return msg


#########################################################################
## DEFINE DATABASE
#########################################################################

# Define Base Tales
db.define_table('vocab',
    Field('value', 'string', unique=True),
    format='%(value)s'
    )
db.define_table('nodeType',
    Field('value', 'string'),
    Field('value_node', 'string'),
    Field('public', 'boolean'),
    Field('required_vocab', 'list:reference vocab'),
    Field('cat_header','text'),
    format='%(value)s'
    )

# Define Compound Tables
db.define_table('node',
    Field('type', db.nodeType, writable=False, readable=False),
    Field('name', 'string', requires=IS_NOT_EMPTY(), label="Name", comment="The Name of the Page"),
    Field('url', unique=True, label="String ID",
                 comment="This is the ID of the page used in the url. Pick a simple and unique alphanumeric id for the page (Numbers, Letters, and Underscores are allowed)."),
    Field('picFile','upload', label="Picture", comment="The display picture of the page.", autodelete=True, requires=IS_NULL_OR(IS_IMAGE(maxsize=(2400, 2400),error_message="Must be an image smaller then 2400px by 2400px"))),
    Field('description','text', label="Page Description", default="",
          comment="This is the text displayed on the page."),
    Field('date', 'datetime', writable=False, readable=False, default=request.now),
    Field('modified', 'datetime', writable=False, readable=False, default=request.now, update=request.now),
    Field('modified_by','integer', default=auth.user_id,update=auth.user_id,writable=False,readable=False),
    Field('tags', 'list:string', label='Keywords', comment="A list of words that describe this node.Press enter in the text box to add another keyword"),
    format='%(name)s'
    )
db.node.url.requires = [IS_NOT_EMPTY(), IS_ALPHANUMERIC(), IS_NOT_IN_DB(db, 'node.url')]
db.node.type.requires = IS_IN_DB(db,db.nodeType.id,'%(value)s')


db.define_table('nodeAttr',
    Field('nodeId', db.node, writable=False, readable=False),
    Field('vocab', db.vocab, label="Section Title", comment="Select the type of information you wish to display."),
    Field('value', 'text', label="Section Text", comment="This is where you write the content of the attribute."),
    Field('weight', 'integer', default=0, label="Display Weight", readable=False, writable=False),
    Field('created', 'datetime', writable=False, readable=False, default=request.now),
    Field('modified', 'datetime', writable=False, readable=False, default=request.now, update=request.now),
    Field('modified_by','integer', default=auth.user_id,update=auth.user_id,writable=False, readable=False),
    format='%(nodeId)s: %(vocab)s'
    )
    
db.nodeAttr.vocab.requires = IS_IN_DB(db,db.vocab.id,'%(value)s')
db.nodeAttr.nodeId.requires = IS_IN_DB(db,db.node.id,'%(name)s (%(url)s)')
db.nodeAttr.vocab.widget = SQLFORM.widgets.autocomplete(request, db.vocab.value, id_field=db.vocab.id, limitby=(0,10), min_length=1)

db.define_table('linkTable',
    Field('nodeId', db.node),
    Field('linkId', db.node),
    Field('date', 'datetime', writable=False, readable=False, default=request.now),
    Field('modified_by','integer', default=auth.user_id,update=auth.user_id,writable=False, readable=False),
    format='%(nodeId)s -> %(linkId)s'
    )

db.linkTable.nodeId.requires = IS_IN_DB(db,db.node.id,'%(name)s (%(url)s)')
db.linkTable.linkId.requires = IS_IN_DB(db,db.node.id,'%(name)s (%(url)s)')
# TODO, ADD MORE CHECKS that prevent multiple records


db.define_table('feedback',
    Field('user_input', 'text'),
    Field('user', 'integer', default=auth.user_id, writable=False, readable=False),
    Field('date', writable=False, readable=False, default=request.now))

db.define_table('syslog',
    Field('date', 'datetime', writable=False, readable=False, default=request.now),
    Field('user','integer', default=auth.user_id,update=auth.user_id,writable=False, readable=False),
    Field('action', requires=IS_IN_SET(
            (
                'Linked Page',
                'Unlinked Page',
                'Added Page',
                'Deleted Page',
                'Added Attribute',
                'Edited Attribute',
                'Deleted Attribute',
            )
        ) ),
    Field('target', 'integer'),
    Field('target2'),
    Field('string_cache', compute=log_str_auto_compute),
    )
#########################################################################
## Authentication
#########################################################################
# CUSTOM AUTH TABLE
auth_table = db.define_table(
    auth.settings.table_user_name,
    Field('first_name', length=128, default=''),
    Field('last_name', length=128, default=''),
    Field('username', unique=True),
    Field('email', length=512, default='', label=auth.messages.label_email),
    Field('password', 'password', length=512, readable=False, label='Password'),
    Field('registration_key', length=512, writable=False, readable=False, default=''),
    Field('registration_id', length=512, writable=False, readable=False, default=''),
    Field('home_node', db.node, writable=False, readable=False),
    Field('watch_nodes', 'list:reference node', readable=False, writable=False),
    Field('email_watch', 'boolean', default=True, readable=False, writable=False),
    )

auth_table.first_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
#auth_table.last_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
auth_table.password.requires = [CRYPT()]
auth_table.username.requires = [IS_LOWER(), IS_NOT_IN_DB(db, auth_table.username)]

auth_table.home_node.requires=IS_NULL_OR(IS_IN_DB(db,db.node.id, '%(name)s (%(url)s)'))

# Gets around circular dependancies
db.node.modified_by.requires=IS_IN_DB(db, auth_table.id, '%(username)s')
db.node.modified_by.represent = lambda id: db.auth_user(id).username
db.nodeAttr.modified_by.requires=IS_IN_DB(db, auth_table.id, '%(username)s')
db.nodeAttr.modified_by.represent = lambda id: db.auth_user(id).username
db.linkTable.modified_by.requires=IS_IN_DB(db, auth_table.id, '%(username)s')
db.linkTable.modified_by.represent = lambda id: db.auth_user(id).username
db.feedback.user.requires=IS_IN_DB(db, auth_table.id, '%(username)s')
db.feedback.user.represent = lambda id: db.auth_user(id).username


auth.settings.hmac_key = 'sha512:54d50bdb-f5f5-4878-8f8f-af19f2f49e5b'   # before define_tables()
auth.define_tables(username=True)                           # creates all needed tables


## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
from gluon.tools import Crud, Service
crud = Crud(globals(),db)                      # for CRUD helpers using auth
service = Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
crud.settings.auth = None                      # =auth to enforce authorization on crud

##
# If it is their first login, they will not have a home node, we must
# Create a node for them and add it to the database
if auth.is_logged_in():

    # Make sure the user has a home node if not create one
    if not auth.user.home_node:
        url = auth.user.username
        
        while db(db.node.url == url).count():
            url = "%s_" % url
            
        id = db.node.insert(
             type=1, name=auth.user.username, url=url,
             description="%s is a lovely person, but they have not had a chance to customize this." % str(auth.user.username) )
        db(auth_table.id == auth.user.id).update(home_node = id)
        auth.user.home_node = id
        
        #Give them an email attribute (6 is email)
        
        if auth.user.email == "":
            email = "%s@rit.edu" % auth.user.username
        else:
            email = auth.user.email
        db.nodeAttr.insert(nodeId=id, vocab=6, value=email)
        
        redirect( URL("main","node",args=url ))


def get_home_node():
    if auth.user.home_node:
        return db(db.node.id == auth.user.home_node).select().first()
        
def can_edit(node):
    if auth.is_logged_in() and (node.type.public or node.id == auth.user.home_node):
        return True
    return False

def is_linked(node1, node2):
    return db((db.linkTable.nodeId == node1) & (db.linkTable.linkId == node2)).count() or \
           db((db.linkTable.nodeId == node2) & (db.linkTable.linkId == node1)).count()

def get_node_links(current_node):
    ## Grab nodes from Linked Table ##
    ######TODO: THIS IS VERY UGLY, combine these into one statement
    ######      so we don't need to do the rows lookup and dive directly
    ######      into the formating statement
    

    # This loops through both sides of the link table
    # adding each item to cat_dict which is a dictionary
    # of categories that hold lists of nodes
    cat_dict = {}
    
    #grab rows where nodeId == node.id
    for row in db(db.linkTable.nodeId==current_node).select():
    
        # if the category has not been seen, add it to the dict with an empty list
        if not cat_dict.has_key(row.linkId.type.value):
            cat_dict[row.linkId.type.value] = []
        
        cat_dict[row.linkId.type.value].append(row.linkId)

    #grab rows where linkId == node.id
    for row in db(db.linkTable.linkId == current_node).select():
    
        # if the category has not been seen, add it to the dict with an empty list
        if not cat_dict.has_key(row.nodeId.type.value):
             cat_dict[row.nodeId.type.value] = []
        cat_dict[row.nodeId.type.value].append(row.nodeId)
        
    return cat_dict

def populate_node_with_required( node ):
    for type in node.type.required_vocab:
        db.nodeAttr.insert(nodeId=node.id, vocab=type, value="Change Me!")
        

### EDIT HELPERS
def get_node_or_404( node_url ):
    node = db(db.node.url == node_url).select().first()
    
    if not node:
        raise HTTP(404, 'node not found')
    else:
        return node
        
def get_attribute_or_404( node, attribute_id ):
    attr = db( (db.nodeAttr.id == attribute_id) & (db.nodeAttr.nodeId == node) ).select().first()
    
    if not attr:
        raise HTTP(404, 'attribute not found')
    else:
        return attr

ALLOWED_HTML_TAGS = [
    'a',
    'b',
    'blockquote',
    'br/',
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
    'td',
    'hr',
    's',
    'sub',
    'sup',
    'div',
    'h1',
    'h2',
    'h3',
    'span',
    'font',
    'strong',
    #Flash Movies
    'object',
    'param',
    'embed',
 ] 

ALLOWED_HTML_ATTR = {
    'a': ['href', 'title', 'style'],
    'img': ['src', 'alt', 'style'],
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
 }
