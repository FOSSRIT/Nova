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
auth.settings.actions_disabled=['register','change_password','request_reset_password','retrieve_username','verify_email','profile']
#########################################################################
## DEFINE DATABASE
#########################################################################

# Define Base Tales
db.define_table('nodeType', Field('value', 'string'), Field('public', 'boolean'))
db.define_table('vocab', Field('value', 'string', unique=True))

# Define Compound Tables
db.define_table('node',
    Field('type', db.nodeType, writable=False, readable=False),
    Field('name', 'string', requires=IS_NOT_EMPTY(), label="Name"),
    Field('url', unique=True, label="Page Url",
                 comment="Customize this node’s URL."),
    Field('picURL','string', label="Picture Url",
                 comment="Provide an URL for this Page's Image."),
    Field('description','text', label="Page Description", default=""),
    Field('date', 'datetime', writable=False, readable=False, default=request.now),
    Field('modified', 'datetime', writable=False, readable=False, default=request.now, update=request.now),
    Field('modified_by','integer', default=auth.user_id,update=auth.user_id,writable=False,readable=False))
db.node.url.requires = [IS_NOT_EMPTY(), IS_ALPHANUMERIC(), IS_NOT_IN_DB(db, 'node.url')]
db.node.type.requires = IS_IN_DB(db,db.nodeType.id,'%(value)s')


db.define_table('nodeAttr',
    Field('nodeId', db.node, writable=False, readable=False),
    Field('vocab', db.vocab),
    Field('value'),
    Field('created', 'datetime', writable=False, readable=False, default=request.now),
    Field('modified', 'datetime', writable=False, readable=False, default=request.now, update=request.now),
    Field('modified_by','integer', default=auth.user_id,update=auth.user_id,writable=False, readable=False))
    
db.nodeAttr.vocab.requires = IS_IN_DB(db,db.vocab.id,'%(value)s')
db.nodeAttr.nodeId.requires = IS_IN_DB(db,db.node.id,'%(name)s (%(url)s)')

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
    Field('password', 'password', length=512, readable=False, label='Password'),
    Field('registration_key', length=512, writable=False, readable=False, default=''),
    Field('registration_id', length=512, writable=False, readable=False, default=''),
    Field('home_node', db.node, writable=False, readable=False),
    Field('in_beta', 'boolean', default=False))

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
        from datetime import datetime
        id = db.node.insert( type=1, name=auth.user.username, url=auth.user.username, date=datetime.now() )
        db(auth_table.id == auth.user.id).update(home_node = id)
        auth.user.home_node = id


def get_home_node():
    if auth.user.home_node:
        return db(db.node.id == auth.user.home_node).select().first()
