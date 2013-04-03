# -*- coding: utf-8 -*- 

#####
# NOTE: Migrate DISABLED in settings.py, enable if making db changes
#####

if request.vars.username:
        request.vars.username = request.vars.username.lower()
if request.post_vars.username:
        request.post_vars.username = request.post_vars.username.lower()

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
    Field('icon','upload', label="Icon", autodelete=True, 
        requires=IS_IMAGE(maxsize=(2400, 2400),error_message="Must be an image smaller then 2400px by 2400px")),
    format='%(value)s'
    )

# Define Compound Tables
db.define_table('node',
    Field('type', db.nodeType, writable=False, readable=False),
    Field('name', 'string', requires=IS_NOT_EMPTY(), label="Name", comment="The Name of the Page"),
    Field('url', unique=True, label="OneWordID",
                 comment="This is the ID of the page used in the url. Pick a simple and unique alphanumeric id for the page (Numbers, Letters, and Underscores are allowed)."),
    Field('picFile','upload', label="Picture", comment="The display picture of the page.", autodelete=True, requires=IS_NULL_OR(IS_IMAGE(maxsize=(2400, 2400),error_message="Must be an image smaller then 2400px by 2400px"))),
    Field('description','text', label="Page Description", default="",
          comment="This is the text displayed on the page."),
    Field('date', 'datetime', writable=False, readable=False, default=request.now),
    Field('modified', 'datetime', writable=False, readable=False, default=request.now, update=request.now),
    Field('modified_by','integer', default=auth.user_id,update=auth.user_id,writable=False,readable=False),
    Field('tags', 'list:string', label='Keywords', comment="A list of words that describe this node. One tag per box. Press enter in the text box to get another box."),
    Field('feeds', 'list:reference rss_feed', label="External Feeds", comment="A list of RSS feeds related to the page.  One feed per box, press enter to add more boxes.", writable=False,readable=False),
    Field('sortOrder', 'integer', writable=False, readable=False, default=0,
        comment="ADMIN SORT ORDER. Set to 0 for natural sort... higher number shows up first"),
    Field('archived', 'boolean', default=False, writable=False, readable=False),
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

db.define_table('blog',
    Field('nodeId', db.node, writable=False, readable=False),
    Field('title', 'string', required=True, requires=IS_NOT_EMPTY()),
    Field('body', 'text'),
    Field('date', 'datetime', writable=False, readable=False, default=request.now),
    Field('author','integer', default=auth.user_id, writable=False, readable=False),
    Field('tags', 'list:string', label='Keywords', comment="A list of words that describe this node. One tag per box. Press enter in the text box to get another box."),
    format='%(nodeId)s: Post: %(title)s'
    )
    

db.define_table('feedback',
    Field('user_input', 'text'),
    Field('user', 'integer', default=auth.user_id, writable=False, readable=False),
    Field('date', writable=False, readable=False, default=request.now))
    
db.define_table('highlights',
    Field('title'),
    Field('weight', 'integer'),
    Field('nodes', 'list:reference node'),
    format='%(title)s',
)

import os
import Image

def checkImage(imgpath):
    try:
        Image.open(imgpath)
        return True
    except:
        return False

db.define_table('filebox',
    Field('Name', requires=IS_NOT_EMPTY(), comment="(Optional, will default to filename on upload)"),
    Field('File','upload', autodelete=True, required=True, requires=IS_LENGTH(MAX_UPLOAD_SIZE, error_message="File must be less then %s" % MAX_SIZE_ENG)),
    Field('size','integer', compute=lambda x: os.path.getsize(os.path.join(request.folder, "uploads", x['File']))),
    Field('image','boolean', compute=lambda x: checkImage( os.path.join(request.folder, "uploads", x['File'])) ),
    Field('owner', default = auth.user_id, writable=False, readable=False),
)



db.define_table('matchingCategory',
    Field('name', 'string', unique=True, required=True),
    Field('namePlural', 'string', unique=True, required=True),
    Field('help_text', 'text', required=False),
    format='%(name)s'
)
    
db.define_table('matchingAttribute',
    Field('category', db.matchingCategory, writable=False, readable=False),
    Field('node', db.node, writable=False, readable=False),
    Field('value', 'string',
        requires=IS_MATCH("^[A-Za-z0-9]+(?:[\s-][A-Za-z0-9]+)*$", error_message="Alphanumeric and non consecutive white space"), required=True),
    Field('provides', 'boolean', writable=False, readable=False, comment="Check if node provides, uncheck if node is looking for"),
    Field('description', 'text', required=False, comment="(Optional) Feel free to provide more information"),
    auth.signature,
    format="%(node.name)s %(value)s"
)
db.matchingAttribute._enable_record_versioning()
     
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
    #BugFIX?
    Field('remember', readable=False, writable=False),
    Field('optout', 'boolean', label="Opt Out of our Announcement Emails",
            comment="Check to Block Announcement Emails", default=False),
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
        
        #have them watch their page
        db(db.auth_user.id == auth.user.id).update(watch_nodes=[id])
        session.auth.user.watch_nodes = [id]
        
        #Give them an email attribute (6 is email)
        
        if auth.user.email == "":
            email = "%s@rit.edu" % auth.user.username
        else:
            email = auth.user.email
        db.nodeAttr.insert(nodeId=id, vocab=6, value=email)
        
        redirect( URL("main","node",args=url ))
