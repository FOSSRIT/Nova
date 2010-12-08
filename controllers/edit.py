# coding: utf8
# try something like
from datetime import datetime
import os.path

def index(): return dict(message="hello from edit.py")

@auth.requires_login()
def link_me():
    node = get_node_or_404( request.args(1) )
    
    if request.args(0) == "add":
        db.linkTable.insert(nodeId=auth.user.home_node, linkId=node.id)
        db.syslog.insert(action="Linked Page", target=auth.user.home_node, target2=node.id)
        session.flash = "Link Added"
        redirect(URL('main','node',args=node.url))          
    elif request.args(0) == "remove":
            db((db.linkTable.nodeId == node) & (db.linkTable.linkId == auth.user.home_node)).delete()
            db((db.linkTable.nodeId == auth.user.home_node) & (db.linkTable.linkId==node)).delete()
            db.syslog.insert(action="Unlinked Page", target=auth.user.home_node, target2=node.id)
            session.flash = "Link Removed"
            redirect(URL('main','node',args=node.url))
    else:
        raise HTTP(405, 'Could not process request')

@auth.requires_login()
def take_picture():
    node = get_node_or_404( request.args(1) )

    # Check node permissions
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node")
                
    if request.vars.do_upload:
        node.update_record(picFile=db.node.picFile.store(request.body,'%s.jpg'% node.id))
        db.syslog.insert(action="Edited Page", target=node.id, target2="photo")
            
        response.view = "generic.load"
        return dict(url=IMG(_src=URL('default','download',args=node.picFile)))
    
    else:
        t = open("/tmp/web2py_upload__%s" % auth.user.username, "w")
        t.write( request.body.read() )
        
        session.tmp_node_file = t.name
        response.view = "generic.load"
        return "File Uploaded"
    
    

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
        if not can_edit(node):
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
                    db.syslog.insert(action="Deleted Attribute", target=node.id, target2=key[5:])
                        
                    # A small Cleanup Routine, check if attriubte is
                    # still in use, if not delete the attribue
                    thecount = db(db.nodeAttr.vocab==vocab).count()
                    if thecount == 0:
                        db(db.vocab.id==vocab.id).delete()
                    
                else:
                    #TODO: protect against misc hits
                    db(db.nodeAttr.id==key[5:]).update(value=attr)
      
        # Process NODE SQL FORM
        form = SQLFORM(db.node, node, deletable=node.type.public, showid = False)
        
        attribute_form = SQLFORM(db.nodeAttr)
        attribute_form.vars.nodeId = node
        
        # Node found, Check and submit to db if needed
        if form.accepts(request.vars):
            if form.vars.delete_this_record:
                session.flash = 'Node Deleted'
                db.syslog.insert(action="Deleted Page", target=node.id)
                
                redirect(URL('main','index'))
            else:
                session.flash = 'form accepted'
                db.syslog.insert(action="Edited Page", target=node.id)
                
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
                if session.tmp_node_file:
                    #TODO: CHECK IF UPLOADED INSTEAD
                    node = db(db.node.url == form.vars.url).select().first()
                    f = open(session.tmp_node_file, 'r')
                    node.update_record(picFile=db.node.picFile.store(f,'%s.jpg'% node.id))
                    f.close()
                    del session.tmp_node_file
                    os.unlink(f.name)
                    
                # Populate Node with required Attributes
                node = db(db.node.url == form.vars.url).select().first()
                populate_node_with_required(node)
                
                db.syslog.insert(action="Added Page", target=node.id)
                
                # Link user node to page
                db.linkTable.insert(nodeId=auth.user.home_node, linkId=node.id)
                
                # Set Watch Node
                add_rem_watch(node, True)
                
                redirect(URL('main','node',args=form.vars.url))
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
    node = get_node_or_404(request.args(0))
        
    # Apply Changes if link requested
    if request.vars.unlinkNode:
        db((db.linkTable.nodeId == node) & (db.linkTable.linkId == int(request.vars.unlinkNode))).delete()
        db((db.linkTable.nodeId == int(request.vars.unlinkNode)) & (db.linkTable.linkId==node)).delete() 
    # Select all nodes that can be linked
    # While we are finding possible links, keep a list of nodes that we do have linked
    nodeSet = []
    linkedSet = []
    
    for row in db(db.node.id != node.id).select(orderby=db.node.name.lower()):
        # Filter out existing links
        if is_linked(node, row):
            linkedSet.append(row)

    cats = db(db.nodeType.value!=None).select()
    return dict( node=node, linkedSet=linkedSet, categories=cats )

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
def blog():
    node = get_node_or_404(request.args(0))
    
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node's Blog")
    
    blog_entry = db( (db.blog.nodeId == node.id) & (db.blog.id == request.args(1) )).select().first()
    form = SQLFORM(db.blog, blog_entry, deletable=True)
    form.vars.nodeId = node
    
    if form.accepts(request.vars, dbio=False):
        if blog_entry:
            if form.vars.get('delete_this_record'):
                db.syslog.insert(action="Deleted Blog Entry", target=node.id, target2=blog_entry.id)
                session.flash = "Blog entry deleted"
                db(db.blog.id==blog_entry.id).delete()
            else:
                blog_entry.update_record(**db.blog._filter_fields(form.vars))
                db.syslog.insert(action="Edited Blog Entry", target=node.id, target2=blog_entry.id)
                session.flash = "Blog entry edited"
        else:
            a_id = db.blog.insert(**db.blog._filter_fields(form.vars))
            db.syslog.insert(action="Added Blog Entry", target=node.id, target2=a_id)
            session.flash = "Blog entry posted"
        
           
        redirect( URL('main','blog',args=node.url) )
    return dict(form=form,node=node)

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
