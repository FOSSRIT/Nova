# coding: utf8
def get_home_node():
    if auth.user.home_node:
        return db(db.node.id == auth.user.home_node).select().first()
        
def get_home_from_user(userid):
    user = db(db.auth_user.id == userid).select().first()
    if user:
        return db(db.node.id == user.home_node).select().first()
    else:
        raise HTTP(404, "User Page not found")
                
def can_edit(node):
    if auth.is_logged_in() and (node.type.public or node.id == auth.user.home_node):
        return True
    elif auth.has_membership("Site Admin"):
        return True
    return False

def is_linked(node1, node2):
    return db((db.linkTable.nodeId == node1) & (db.linkTable.linkId == node2)).count() or \
           db((db.linkTable.nodeId == node2) & (db.linkTable.linkId == node1)).count()

def get_node_links(current_node):
    ## Grab nodes from Linked Table ##
    ######TODO: THIS IS VERY UGLY, combine these into one statement
    ######      so we don't need to do the rows lookup and dive directly
    ######      into the formating statement
    

    # This loops through both sides of the link table
    # adding each item to cat_dict which is a dictionary
    # of categories that hold lists of nodes
    cat_dict = {}
    
    #grab rows where nodeId == node.id
    for row in db(db.linkTable.nodeId==current_node).select():
    
        # if the category has not been seen, add it to the dict with an empty list
        if not cat_dict.has_key(row.linkId.type.value):
            cat_dict[row.linkId.type.value] = []
        
        cat_dict[row.linkId.type.value].append(row.linkId)

    #grab rows where linkId == node.id
    for row in db(db.linkTable.linkId == current_node).select():
    
        # if the category has not been seen, add it to the dict with an empty list
        if not cat_dict.has_key(row.nodeId.type.value):
             cat_dict[row.nodeId.type.value] = []
        cat_dict[row.nodeId.type.value].append(row.nodeId)
        
    return cat_dict

def populate_node_with_required( node ):
    for type in node.type.required_vocab:
        db.nodeAttr.insert(nodeId=node.id, vocab=type, value="Change Me!")
        

### EDIT HELPERS
def get_node_or_404( node_url ):
    node = db(db.node.url == node_url).select().first()
    
    if not node:
        raise HTTP(404, 'node not found')
    else:
        return node
        
def get_attribute_or_404( node, attribute_id ):
    attr = db( (db.nodeAttr.id == attribute_id) & (db.nodeAttr.nodeId == node) ).select().first()
    
    if not attr:
        raise HTTP(404, 'attribute not found')
    else:
        return attr
