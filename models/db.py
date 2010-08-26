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
crud = Crud(globals(),db)                      # for CRUD helpers using auth
service = Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc

auth.settings.hmac_key = 'sha512:54d50bdb-f5f5-4878-8f8f-af19f2f49e5b'   # before define_tables()
auth.define_tables()                           # creates all needed tables
auth.settings.registration_requires_approval = False
crud.settings.auth = None                      # =auth to enforce authorization on crud

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
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
