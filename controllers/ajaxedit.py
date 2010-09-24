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
        
        attr = db(db.nodeAttr.id == attr ).select().first()
        
        return dict(t=MARKMIN(attr.value))

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
        
    attribute_form = SQLFORM(db.nodeAttr,submit_button="Save",_action = URL('ajaxedit','addattribute', args=[node.url]))
    attribute_form.vars.nodeId = node
    
    # If they entered custom text, it will have vocab as '' and the auto complete will not be empty
    if( request.vars.vocab == '' and request.vars._autocomplete_value_aux != '' ):
        # TODO Check content is valid
        request.vars.vocab = db.vocab.insert(value=request.vars._autocomplete_value_aux)
        attribute_form.vars.vocab = request.vars.vocab
            
    if attribute_form.accepts(request.vars):
        response.view = "htmlblocks/attributes.html"
        attr = db(db.nodeAttr.nodeId==node).select(orderby=db.nodeAttr.weight)
        return dict(node_attributes=attr)
    else:
        attrlist = db(db.vocab.id>0).select()
    
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
        return dict(node=MARKMIN(node.get(request.args(1))))
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
        return dict(t=IMG(_src=URL('default','download',args=node.picFile)))
            
    else:
        response.view = "htmlblocks/edit_pict_form.html"
        return dict(node=node, form=form)
