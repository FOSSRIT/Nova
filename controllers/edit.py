# coding: utf8
# try something like
from datetime import datetime
import os.path

def index(): return dict(message="hello from edit.py")

@auth.requires_login()
def link_me():
    node = None
    try:
        node = db(db.node.url == request.args[1]).select().first()
    except:
        raise HTTP(404, 'node not found')
    
    if node and request.args[0]:
        if request.args[0] == "add":
            db.linkTable.insert(nodeId=auth.user.home_node, linkId=node.id)
            session.flash = "Link Added"
            redirect(URL('main','node',args=node.url))          
        elif request.args[0] == "remove":
            db((db.linkTable.nodeId == node) & (db.linkTable.linkId == auth.user.home_node)).delete()
            db((db.linkTable.nodeId == auth.user.home_node) & (db.linkTable.linkId==node)).delete()
            session.flash = "Link Removed"
            redirect(URL('main','node',args=node.url))
    else:
        raise HTTP(404, 'Could not process request')

@auth.requires_login()
def take_picture():
    node = None
    if len(request.args):
        try:
            node = db(db.node.url == request.args[0]).select().first()
        except:
            raise HTTP(404, 'node not found')

    if node:
        # Make sure they are not trying to edit someone's node
        # TODO ADD PERMISSION SYSTEM HERE
        if node.type.public == False and node.id != auth.user.home_node:
            raise HTTP(403, "Not Authorized to edit this node")
            
        if request.vars.do_upload:
            node.update_record(picFile=db.node.picFile.store(request.body,'%s.jpg'% node.id))
        
            response.view = "generic.load"
            return dict(url="uploaded")

    else:
        raise HTTP(404, 'node not found')

    return dict(node=node)

@auth.requires_login()
def in_place():
    try:
        node = db(db.node.url == request.args[0]).select().first()
    except:
        raise HTTP(404, 'node not found')
    try:
        if request.args[1].startswith("attr_"):
            attr = db(db.nodeAttr.id == int(request.args[1][5:])).select().first()
            if attr:
                form = SQLFORM( db.nodeAttr, attr, showid = False,
                                comments=False, fields=['value','weight'], labels={'value':""},
                                _action = URL('edit','in_place', args=[node.url,request.args[1]]))
                
            else:
                raise HTTP(404, "Attribute not found")
                    
        else:
            form = SQLFORM( db.node, node, fields=[request.args[1]], labels={request.args[1]:""},
                        comments=False, formstyle="divs" , showid = False,
                        _action = URL('edit','in_place', args=[node.url,request.args[1]]) )
    except:
        raise HTTP(404, "Field Not Found")
        
    response.view = "generic.load"
    if form.accepts(request.vars):
        # Get updated node information
        if request.args[1].startswith("attr_"):
            attr = db(db.nodeAttr.id == int(request.args[1][5:])).select().first()
            
            return dict(t=MARKMIN(attr.value))
        else:
            node = db(db.node.url == request.args[0]).select().first()
            return dict(node=MARKMIN(node.get(request.args[1])))
    else:
        return dict(form=form)
    
    

@auth.requires_login()
def node():
    """
    Display a node edit form.  If request has an id, it will attempt to
    pull the id from the database and allow the view to populate with
    the correct data.
    
    View will get node.  Node may be none, it is up to the view to detect
    and correctly handle an empty node (It will be making a new node)
    """   
    
    # Now we want to populate the response
    node = None
    attr = None
    attribute_form = None

    # If requested a node in the url, pull from the database
    if len(request.args):
        try:
            node = db(db.node.url == request.args[0]).select().first()
        except:
            pass
        
    if node:
        # Make sure they are not trying to edit someone's node
        # TODO ADD PERMISSION SYSTEM HERE
        if node.type.public == False and node.id != auth.user.home_node:
            raise HTTP(403, "Not Authorized to edit this node")
    
        # Update all the attributes if they exist
        # This must be done before attribute form is created
        # TODO NEED TO ADD SECURITY FOR THIS LOOP
        for key,attr in request.vars.items():
            
            # All attributes start with attr. then the key
            if key.startswith('attr.'):
                
                if attr == "":
                    vocab = db(db.nodeAttr.id == key[5:]).select()[0].vocab
                    db(db.nodeAttr.id==key[5:]).delete()
                        
                    # A small Cleanup Routine, check if attriubte is
                    # still in use, if not delete the attribue
                    thecount = db(db.nodeAttr.vocab==vocab).count()
                    if thecount == 0:
                        db(db.vocab.id==vocab.id).delete()
                    
                else:
                    #TODO: protect against misc hits
                    db(db.nodeAttr.id==key[5:]).update(value=attr)
      
        # Process NODE SQL FORM
        form = SQLFORM(db.node, node, deletable=node.type.public)
        
        attribute_form = SQLFORM(db.nodeAttr)
        attribute_form.vars.nodeId = node
        
        # Node found, Check and submit to db if needed
        if form.accepts(request.vars):
            if form.vars.delete_this_record:
                session.flash = 'Node Deleted'
                redirect(URL('main','index'))
            else:
                session.flash = 'form accepted'
                redirect(URL('edit','node',args=form.vars.url))
        elif form.errors:
            response.flash = 'form has errors'
            
        if attribute_form.accepts(request.vars):
            response.flash = 'Attribute Form accepted'
        elif attribute_form.errors:
            response.flash = 'Attribute Form has errors'
            
        # Get Attribute List
        attr = db(db.nodeAttr.nodeId==node).select()
        
    elif not node and request.vars.type:
        type = db(db.nodeType.value==request.vars.type).select().first()
        if type and type.public:
            form = SQLFORM(db.node, node)
            form.vars.type=type
            form.vars.date=datetime.now()
             
            if form.accepts(request.vars):
                session.flash = 'form accepted'
                redirect(URL('edit','node',args=form.vars.url))
            elif form.errors:
                response.flash = 'form has errors'

        else:
            raise HTTP(404, "Type Not Found")
    else:
        #No node found and no type requested (BAD)
        raise HTTP(404, "No node requested, no type requested")
    
    return dict(node=node, attr=attr, form=form, attribute_form=attribute_form)

@auth.requires_login()
def link():
    """
    Shows list of all nodes that can be linked with current node as
    well as links any nodes requested.
    
    TODO: This is a temporary way as the the number of nodes increases,
    this function will get out of control in its current state.  A better
    way must be used then displaying all nodes and let them choose.
    """
    try:
        node = db(db.node.url == request.args[0]).select()[0]
    except:
        raise HTTP(404, "Node Not Found")
        
    # Apply Changes if link requested
    if request.vars.linkNode:
        db.linkTable.insert(nodeId=node, linkId=int(request.vars.linkNode), date=datetime.now())
        response.flash = "Link Added"
        
    if request.vars.unlinkNode:
        db((db.linkTable.nodeId == node) & (db.linkTable.linkId == int(request.vars.unlinkNode))).delete()
        db((db.linkTable.nodeId == int(request.vars.unlinkNode)) & (db.linkTable.linkId==node)).delete() 
    # Select all nodes that can be linked
    # While we are finding possible links, keep a list of nodes that we do have linked
    nodeSet = []
    linkedSet = []
    
    for row in db(db.node.id != node.id).select():
        # Filter out existing links
        if is_linked(node, row):
            linkedSet.append(row)
            
        else:
            nodeSet.append(row)

    return dict( node=node, nodeSet=nodeSet, linkedSet=linkedSet )

def category():
    return dict(message="hello from edit.py")

@auth.requires_login()
def attribute_vocab():
    """
    Displays A form to allow people to add new attribute vocab
    """
    vocab_form = SQLFORM(db.vocab)
    if vocab_form.accepts(request.vars, session):
        response.flash = 'New Attribute accepted'
    elif vocab_form .errors:
        response.flash = 'New Attribute has errors'
    return dict(vocab_form=vocab_form)

@auth.requires_login()
def feedback():
    """
    Display and saves from feedback from
    """
    form = SQLFORM(db.feedback, labels={'user_input':""})
    
    # Check and submit to db if needed
    if form.accepts(request.vars):
        response.flash = 'Thankyou for your feedback'
    
    return dict(form=form)
