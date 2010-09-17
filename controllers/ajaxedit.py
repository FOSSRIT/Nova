# coding: utf8

@auth.requires_login()
def editattribute():
    # Find the node we are trying to update
    try:
        node = db(db.node.url == request.args[0]).select().first()
    except:
        raise HTTP(404, 'node not found')
    
    if not node:
        raise HTTP(404, 'node not found')
        
    # Check node permissions
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node's Attribute")
    
    # Get attribute we are trying to update
    try:
        attr = db( (db.nodeAttr.id == int(request.args[1])) &
                   (db.nodeAttr.nodeId == node) ).select().first()
                   
    except:
        raise HTTP(404, 'attribute not found')
        
    if attr:
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
    else:
        raise HTTP(404, 'attribute not found')
