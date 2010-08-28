# coding: utf8
# try something like
from datetime import datetime

def index(): return dict(message="hello from edit.py")

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
        form = SQLFORM(db.node, node)
        
        attribute_form = SQLFORM(db.nodeAttr)
        attribute_form.vars.nodeId = node
        
        # Node found, Check and submit to db if needed
        if form.accepts(request.vars):
            session.flash = 'form accepted'
            redirect(URL(args=form.vars.url))
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
                response.flash = 'form accepted'
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
    
    # Select all nodes that can be linked
    nodeSet = []
    
    for row in db(db.node.id != node.id).select():
        # Filter out existing links
        if not db((db.linkTable.nodeId == node) & (db.linkTable.linkId == row)).count() and \
           not db((db.linkTable.nodeId == row) & (db.linkTable.linkId == node)).count():
            nodeSet.append(row)

    return dict( node=node, nodeSet=nodeSet )

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
