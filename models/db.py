# -*- coding: utf-8 -*- 

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('gae')                           # connect to Google BigTable
    session.connect(request, response, db = db) # and store sessions and tickets there
    ### or use the following lines to store sessions in Memcache
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
else:                                         # else use a normal relational database
    db = DAL('sqlite://storage.sqlite')       # if not, use SQLite or other DB



#########################################################################
## DEFINE DATABASE
#########################################################################

# Define Base Tales
db.define_table('nodeType', Field('value', 'string'))
db.define_table('vocab', Field('value', 'string', unique=True))

# Define Compound Tables
db.define_table('node',
    Field('type', db.nodeType),
    Field('name', 'string'),
    Field('url', unique=True),
    Field('picURL','string'),
    Field('description','text'),
    Field('date', 'datetime'))

db.define_table('nodeAttr',
    Field('nodeId', db.node),
    Field('vocab', db.vocab),
    Field('value'))
    
db.define_table('linkTable',
    Field('nodeId', db.node),
    Field('linkId', db.node),
    Field('date', 'datetime'))



## if no need for session
# session.forget()

#########################################################################
## Here is sample code if you need for 
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import *
auth = Auth(globals(),db)                      # authentication/authorization
from gluon.contrib.login_methods.ldap_auth import ldap_auth
auth.settings.login_methods.append(ldap_auth(server='ldap.rit.edu', base_dn='ou=people,dc=rit,dc=edu'))

auth.settings.actions_disabled=['register','change_password','request_reset_password']

auth_table = db.define_table(
    auth.settings.table_user_name,
    Field('first_name', length=128, default=''),
    Field('last_name', length=128, default=''),
    Field('username', unique=True, writable=True),
    Field('password', 'password', length=512, readable=False, label='Password'),
    Field('registration_key', length=512, writable=False, readable=False, default=''),
    Field('registration_id', length=512, writable=False, readable=False, default=''),
    Field('home_node', db.node, writable=False, readable=False))

auth_table.first_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
auth_table.last_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
auth_table.password.requires = [ CRYPT()]
auth_table.username.requires = IS_NOT_IN_DB(db, auth_table.username)


crud = Crud(globals(),db)                      # for CRUD helpers using auth
service = Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc

auth.settings.hmac_key = 'sha512:54d50bdb-f5f5-4878-8f8f-af19f2f49e5b'   # before define_tables()
auth.define_tables(username=True)                           # creates all needed tables

if auth.is_logged_in():
    # Make sure the user has a home node if not create one
    if not auth.user.home_node:
        from datetime import datetime
        id = db.node.insert( type=1, name=auth.user.username, url=auth.user.username, date=datetime.now() )
        db(auth_table.id == auth.user.id).update(home_node = id)
        auth.user.home_node = id
        
    
        


crud.settings.auth = None                      # =auth to enforce authorization on crud
