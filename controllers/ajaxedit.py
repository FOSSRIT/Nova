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
                    comments=False, fields=['value','weight'],
                    labels={'value':""},
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
    
    # Return html attribute list
    response.view = "htmlblocks/attributes.html"
    attr_list = db(db.nodeAttr.nodeId==node).select(orderby=db.nodeAttr.weight)
    return dict(node_attributes=attr_list)
