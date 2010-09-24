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
from gluon.tools import *
from gluon.contrib.login_methods.ldap_auth import ldap_auth

auth = Auth(globals(),db)                      # authentication/authorization

# RIT Ldap
auth.settings.login_methods.append(ldap_auth(server='ldap.rit.edu', base_dn='ou=people,dc=rit,dc=edu'))

# DISABLE EXTRA FEATURES
# 
auth.settings.actions_disabled=['register','request_reset_password','retrieve_username','verify_email','profile']
#########################################################################
## DEFINE DATABASE
#########################################################################

# Define Base Tales
db.define_table('nodeType', Field('value', 'string'), Field('public', 'boolean'))
db.define_table('vocab', Field('value', 'string', unique=True))

# Define Compound Tables
db.define_table('node',
    Field('type', db.nodeType, writable=False, readable=False),
    Field('name', 'string', requires=IS_NOT_EMPTY(), label="Name", comment="The Name of the Page"),
    Field('url', unique=True, label="String ID",
                 comment="This is the ID of the page used in the url. Pick a simple and unique alphanumeric id for the page (Numbers, Letters, and Underscores are allowed)."),
    Field('picFile','upload', label="Picture", comment="The display picture of the page.", autodelete=True,),
    Field('description','text', label="Page Description", default="",
          comment="This is the text displayed on the page. You may use MARKMIN syntax in this section."),
    Field('date', 'datetime', writable=False, readable=False, default=request.now),
    Field('modified', 'datetime', writable=False, readable=False, default=request.now, update=request.now),
    Field('modified_by','integer', default=auth.user_id,update=auth.user_id,writable=False,readable=False))
db.node.url.requires = [IS_NOT_EMPTY(), IS_ALPHANUMERIC(), IS_NOT_IN_DB(db, 'node.url')]
db.node.type.requires = IS_IN_DB(db,db.nodeType.id,'%(value)s')


db.define_table('nodeAttr',
    Field('nodeId', db.node, writable=False, readable=False),
    Field('vocab', db.vocab, label="Section Title", comment="Select the type of information you wish to display."),
    Field('value', 'text', label="Section Text", comment="This is where you write the content of the attribute."),
    Field('weight', 'integer', default=0, label="Display Weight", readable=False, writable=False),
    Field('created', 'datetime', writable=False, readable=False, default=request.now),
    Field('modified', 'datetime', writable=False, readable=False, default=request.now, update=request.now),
    Field('modified_by','integer', default=auth.user_id,update=auth.user_id,writable=False, readable=False))
    
db.nodeAttr.vocab.requires = IS_IN_DB(db,db.vocab.id,'%(value)s')
db.nodeAttr.nodeId.requires = IS_IN_DB(db,db.node.id,'%(name)s (%(url)s)')
db.nodeAttr.vocab.widget = SQLFORM.widgets.autocomplete(request, db.vocab.value, id_field=db.vocab.id, limitby=(0,10), min_length=1)

db.define_table('linkTable',
    Field('nodeId', db.node),
    Field('linkId', db.node),
    Field('date', 'datetime', writable=False, readable=False, default=request.now),
    Field('modified_by','integer', default=auth.user_id,update=auth.user_id,writable=False, readable=False))

db.linkTable.nodeId.requires = IS_IN_DB(db,db.node.id,'%(name)s (%(url)s)')
db.linkTable.linkId.requires = IS_IN_DB(db,db.node.id,'%(name)s (%(url)s)')
# TODO, ADD MORE CHECKS that prevent multiple records


db.define_table('feedback',
    Field('user_input', 'text'),
    Field('user', 'integer', default=auth.user_id, writable=False, readable=False),
    Field('date', writable=False, readable=False, default=request.now))

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
    Field('in_beta', 'boolean', default=False, writable=False, readable=False))

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
crud = Crud(globals(),db)                      # for CRUD helpers using auth
service = Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
crud.settings.auth = None                      # =auth to enforce authorization on crud

##
# If it is their first login, they will not have a home node, we must
# Create a node for them and add it to the database
if auth.is_logged_in():
    #if not auth.user.in_beta:
    #    auth.logout(next=URL('default', 'not_in_beta'))

    # Make sure the user has a home node if not create one
    if not auth.user.home_node:
        id = db.node.insert(
             type=1, name=auth.user.username, url=auth.user.username,
             description="%s is a lovely person, but they have not had a chance to customize this." % str(auth.user.username) )
        db(auth_table.id == auth.user.id).update(home_node = id)
        auth.user.home_node = id
        redirect( URL("main","node",args=auth.user.username ))


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
