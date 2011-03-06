# coding: utf8
# try something like
from datetime import datetime
import os.path

def index(): return dict(message="hello from edit.py")

@auth.requires_login()
def dropbox():
    filerecord = db((db.filebox.id == request.args(0)) & (db.filebox.owner == auth.user_id)).select().first()
        
    sum = get_quota_usage()
    
    if not filerecord and sum > MAX_FILE_STORE:
        form = P("You have maxed your upload limit, please delete files in order to upload more.")
    else:
        form=SQLFORM(db.filebox, filerecord, deletable=True, showid=False, upload=URL("default","download"))
        try:
            if request.vars.File != request.vars.File.filename:
                if request.vars.Name == "":
                    form.vars.Name = request.vars.File.filename
                    request.vars.Name = request.vars.File.filename
                    request.post_vars.Name = request.vars.File.filename
        except:
            pass
            
        if form.accepts(request, session):
            session.flash = "Form Accepted"
            sum = get_quota_usage(True)
    
            redirect( URL() )
        elif form.errors:
            response.flash = "Form has errors"
        
    return dict(form=form, files=db(db.filebox.owner == auth.user_id).select(), sum=sum)

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
    node = get_node_or_404( request.args(0) )

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
      
        # Process NODE SQL FORM
        form = SQLFORM(db.node, node, deletable=node.type.public, showid = False)
        
        # Node found, Check and submit to db if needed
        if form.accepts(request.vars):
            if form.vars.delete_this_record:
                session.flash = 'Node Deleted'
                db.syslog.insert(action="Deleted Page", target=node.id)
                
                redirect(URL('main','index'))
            else:
                session.flash = 'form accepted'
                db.syslog.insert(action="Edited Page", target=node.id, target2="Full Page (Unknown, manual form)")
                
                redirect(URL('edit','node',args=form.vars.url))
        elif form.errors:
            response.flash = 'form has errors'
            
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
    
    return dict(node=node, form=form)

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

    return dict( node=node, linkedSet=linkedSet)

def category():
    return dict(message="hello from edit.py")
    
@auth.requires_login()
def batch_tag():
    return dict()
    
@auth.requires_membership("Site Admin")
def home_page():
    linkedSet = db(db.highlights.title == request.args(0).replace("_"," ")).select().first()

    if linkedSet:
        return dict(linkedSet=linkedSet.nodes, category=linkedSet)
    else:
        raise HTTP(404, "No Category Found")

@auth.requires_membership("Site Admin")
def home_page_cat():
    if request.args(0):
        highlight = db(db.highlights.title == request.args(0).replace("_"," ")).select().first()
    else:
        highlight = None
    form = SQLFORM(db.highlights, highlight, deletable=True, showid=False, fields=['title','weight'])
    
    if not highlight:
        form.vars.nodes = []
        
    if form.accepts(request.vars, session):
        redirect( URL('main','index') )
        
    elif form.errors:
        response.flash = form.errors
        
    return dict(form=form)
    
@auth.requires_login()
def attribute_vocab():
    """
    Displays A form to allow people to add new attribute vocab
    """
    vocab_form = SQLFORM(db.vocab)
    if vocab_form.accepts(request.vars, session):
        response.flash = 'New Attribute accepted'
    elif vocab_form.errors:
        response.flash = 'New Attribute has errors'
    return dict(vocab_form=vocab_form)

@auth.requires_login()
def blog():
    node = get_node_or_404(request.args(0))
    
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node's Blog")
    
    blog_entry = db( (db.blog.nodeId == node.id) & (db.blog.id == request.args(1) )).select().first()
    form = SQLFORM(db.blog, blog_entry, deletable=True, formstyle="table2cols")
    form.vars.nodeId = node
    
    if form.accepts(request.vars, dbio=False):
        node.update_record(modified=request.now)
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
