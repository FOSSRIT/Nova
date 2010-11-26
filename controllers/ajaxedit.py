# coding: utf8

@auth.requires_login()
def editattribute():
    """
    Allows users to edit attributes connected to a node.
    
    Exposes: /ajaxedit/editattribute/NODE_URL_ID/attr_ATTRIBUTE_ID
    """
    # Find the node we are trying to update
    node = get_node_or_404( request.args(0) )
        
    # Check node permissions
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node's Attributes")
    
    # Get attribute we are trying to update
    attr = get_attribute_or_404(node, request.args(1)[5:] )
        
    form = SQLFORM( db.nodeAttr, attr, showid = False,
                    comments=False, fields=['value'],#,'weight'],
                    labels={'value':""}, submit_button="Save",
                    _action = URL('ajaxedit','editattribute',
                    args=[node.url,request.args[1]]))

    if form.accepts(request.vars, session):
        response.view = "generic.load"
        db.syslog.insert(action="Edited Attribute", target=node.id, target2=attr.id)
        
        attr = db(db.nodeAttr.id == attr ).select().first()
        
        return dict(t=XML(attr.value,True, ALLOWED_HTML_TAGS, ALLOWED_HTML_ATTR))

    else:
        response.view = "generic.load"
        return dict(form=form)
        
@auth.requires_login()
def deleteattribute():
    """
    Allows users to delete attributes connected to a node.
    
    Exposes: /ajaxedit/deleteattribute/NODE_URL_ID/attrdel_ATTRIBUTE_ID
    """
    # Find the node we are trying to update
    node = get_node_or_404( request.args(0) )
        
    # Check node permissions
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node's Attributes")
    
    # Get attribute we are trying to delete and delete it
    attr = get_attribute_or_404(node, request.args(1)[8:] )
    db(db.nodeAttr.id==attr).delete()
    db.syslog.insert(action="Deleted Attribute", target=node.id, target2=attr.id)
    
    # A small Cleanup Routine, check if attriubte is
    # still in use, if not delete the attribute
    if db(db.nodeAttr.vocab==attr.vocab).count() == 0:
        db(db.vocab.id==attr.vocab.id).delete()
    
    # Return html attribute list
    response.view = "htmlblocks/attributes.html"
    attr_list = db(db.nodeAttr.nodeId==node).select(orderby=db.nodeAttr.weight)
    return dict(node_attributes=attr_list)

@auth.requires_login()
def addattribute():
    # Find the node we are trying to update
    node = get_node_or_404( request.args(0) )
    
    # Check node permissions
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node's Attributes")
        
    attribute_form = SQLFORM(db.nodeAttr,submit_button="Save",_action = URL('ajaxedit','addattribute', args=[node.url]), comments=False)
    attribute_form.vars.nodeId = node
    
    # If they entered custom text, it will have vocab as '' and the auto complete will not be empty
    if( request.vars.vocab == '' and request.vars._autocomplete_value_aux != '' ):
        # TODO Check content is valid
        request.vars.vocab = db.vocab.insert(value=request.vars._autocomplete_value_aux)
        attribute_form.vars.vocab = request.vars.vocab
            
    if attribute_form.accepts(request.vars, dbio=False):
        a_id = db.nodeAttr.insert(**db.nodeAttr._filter_fields(attribute_form.vars))
        response.view = "htmlblocks/attributes.html"
        attr = db(db.nodeAttr.nodeId==node).select(orderby=db.nodeAttr.weight)
        db.syslog.insert(action="Added Attribute", target=node.id, target2=a_id)
        return dict(node_attributes=attr)
    else:
        attrlist = db(db.vocab.id>0).select(orderby=db.vocab.value)
    
        response.view = "htmlblocks/attribute_inplace_form.html"
        return dict(form=attribute_form,attrlist=attrlist)

@auth.requires_login()
def editnode():
    # Find the node we are trying to update
    node = get_node_or_404( request.args(0) )
    
    # Check node permissions
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node")
        
    form = SQLFORM( db.node, node, fields=[request.args(1)], labels={request.args(1):""},
                    comments=False, formstyle="divs" , showid = False, submit_button="Save",
                    _action = URL('ajaxedit','editnode', args=[node.url,request.args(1)]) )
                    
    response.view = "generic.load"
    if form.accepts(request.vars):
        # Grab the new version of the node to populate data
        node = db(db.node.url == request.args(0)).select().first()
        db.syslog.insert(action="Edited Page", target=node.id, target2=request.args(1))
        return dict(node=XML(node.get(request.args(1)),True, ALLOWED_HTML_TAGS, ALLOWED_HTML_ATTR))
    else:
        return dict(form=form)
        
@auth.requires_login()
def editphoto():
    # Find the node we are trying to update
    node = get_node_or_404( request.args(0) )
    
    # Check node permissions
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node")
        
        
    form = SQLFORM( db.node, node, fields=['picFile'], labels={'picFile':""},
                    comments=False, formstyle="divs" , showid = False,
                    _action = URL('ajaxedit','editphoto', args=[node.url]) )
                    
    if form.accepts(request.vars):
        response.view = "generic.load"
        node = db(db.node.url == request.args(0)).select().first()
        db.syslog.insert(action="Edited Page", target=node.id, target2="photo")
        return dict(t=IMG(_src=URL('default','thumb',args=[300,300,node.picFile])))
            
    else:
        response.view = "htmlblocks/edit_pict_form.html"
        return dict(node=node, form=form)

@auth.requires_login()
def link():
    # Find the node we are trying to update
    node = get_node_or_404( request.args(0) )
    node2 = get_node_or_404( request.args(1) )
    
    # Check node permissions
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node")
        
    if is_linked(node, node2):
        raise HTTP(405, "Already Linked")
        
    if node.id == node2.id:
        raise HTTP(405, "Can't Link to Self")
        
    db.linkTable.insert(nodeId=node, linkId=node2)
    db.syslog.insert(action="Linked Page", target=node.id, target2=node2.id)
    raise HTTP(200, "Ok, link made")


@auth.requires_login()
def unlink():
    # Find the node we are trying to update
    node = get_node_or_404( request.args(0) )
    node2 = get_node_or_404( request.args(1) )
    
    # Check node permissions
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node")
        
    db((db.linkTable.nodeId == node) & (db.linkTable.linkId == node2)).delete()
    db((db.linkTable.nodeId == node2) & (db.linkTable.linkId==node)).delete() 
    db.syslog.insert(action="Unlinked Page", target=node.id, target2=node2.id)
        
    raise HTTP(200, "Ok, link removed")

@auth.requires_login()
def watch():
    node = get_node_or_404( request.args(0) )
    the_cid = request.vars.cid or 'watch_link'
    
    # Check if None
    if not auth.user.watch_nodes:
        db(db.auth_user.id == auth.user.id).update(watch_nodes=[node.id])
        session.auth.user.watch_nodes = [node.id]
        
        response.view = "generic.load"
        return A('Unwatch',_href=URL('ajaxedit','unwatch',args=node.url), cid=the_cid)
        
    elif node.id not in auth.user.watch_nodes:
        db(db.auth_user.id == auth.user.id).update(watch_nodes=auth.user.watch_nodes + [node.id])
        session.auth.user.watch_nodes = auth.user.watch_nodes + [node.id]
        
        response.view = "generic.load"
        return A('Unwatch',_href=URL('ajaxedit','unwatch',args=node.url), cid=the_cid)
        
    else:
        raise HTTP(405, 'Already watched')
    
@auth.requires_login()
def unwatch():
    node = get_node_or_404( request.args(0) )
    the_cid = request.vars.cid or 'watch_link'
    
    if node.id in auth.user.watch_nodes:
        auth.user.watch_nodes.remove(node.id)
        db(db.auth_user.id == auth.user.id).update(watch_nodes=auth.user.watch_nodes)
        session.auth.user.watch_nodes = auth.user.watch_nodes
        response.view = "generic.load"
        return A('Watch',_href=URL('ajaxedit','watch',args=node.url), cid=the_cid)
    else:
        raise HTTP(405, 'Not watched')

@auth.requires_login()
def watchemail():
    if request.args(0) == "True":
        auth.user.email_watch = True
        db(db.auth_user.id == auth.user.id).update(email_watch=True)
        session.auth.user.email_watch = True
        response.view = "generic.load"
        return "Daily Email Enabled, " + A('Disable Daily Email', _href=URL('ajaxedit','watchemail',args='False'), cid='watch_email').xml()
    else:
        auth.user.email_watch = False
        db(db.auth_user.id == auth.user.id).update(email_watch=False)
        session.auth.user.email_watch = False
        response.view = "generic.load"
        return "Daily Email Disabled, " + A('Enable Daily Email', _href=URL('ajaxedit','watchemail',args='True'), cid='watch_email').xml()
