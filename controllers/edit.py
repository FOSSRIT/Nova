# coding: utf8
# try something like
def index(): return dict(message="hello from edit.py")

def node():
    """
    Display a node edit form.  If request has an id, it will attempt to
    pull the id from the database and allow the view to populate with
    the correct data.
    
    View will get node.  Node may be none, it is up to the view to detect
    and correctly handle an empty node (It will be making a new node)
    """
    # See if we need to update the database
    if(request.vars):
        if(request.vars.id == 'new'):
            # Create new node with submitted data
            db.node.insert( type=request.vars.nodeType,
                            name=request.vars.name,
                            url=request.vars.url,
                            picURL=request.vars.pic_url,
                            description=request.vars.desc
                          )
            response.flash = "%s Created" % request.vars.name
            
        else:
            # Update Node with submitted data
            db(db.node.id == request.vars.id).update(type=request.vars.nodeType,
                                                     name=request.vars.name,
                                                     url=request.vars.url,
                                                     picURL=request.vars.pic_url,
                                                     description=request.vars.desc
                                                     )
            response.flash = "%s Updated" % request.vars.name

            # Update all the attributes        
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
    
    # Now we want to populate the response
    node = None
    attr = None
    
    # If edited, pull new node data
    if request.vars.url:
        try:
            node = db(db.node.url == request.vars.url).select()[0]
            attr = db(db.nodeAttr.nodeId==node).select()
        except:
            pass
            
    # If requested a node in the url, pull from the database
    elif len(request.args):
        try:
            node = db(db.node.url == request.args[0]).select()[0]
            attr = db(db.nodeAttr.nodeId==node).select()
        except:
            pass
        
    # Get node types to show the user
    node_types = types=db(db.nodeType.id != None).select()
    return dict(types=node_types, node=node, attr=attr)

def category():
    return dict(message="hello from edit.py")
    
def attribute():
    """
    Adds an attribute to a node
    """
    try:
        node = db(db.node.url == request.args[0]).select()[0]
    except:
        raise HTTP(404, "Node Not Found") 
        
    
    # Check to see if we have submitted an attr to add
    if request.vars.attr:  
        db.nodeAttr.insert(nodeId=node, vocab=request.vars.attr, value=request.vars.value)
        response.flash = "Attribute Saved"
        
    # Check if making a new attribute and adding it's data
    elif request.vars.new_attr:
        vocab_id = db.vocab.insert(value=request.vars.new_attr)
        db.nodeAttr.insert(nodeId=node, vocab=vocab_id, value=request.vars.value)
        response.flash = "Attribute Created and Saved"

    # Grab current Attributes for the node and all possible vocab
    attr = db(db.nodeAttr.nodeId == node).select()
    vocab = db(db.vocab.id != None).select()

    return dict(node=node, attr=attr, vocab=vocab)
