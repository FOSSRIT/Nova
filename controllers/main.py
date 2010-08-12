# coding: utf8
# try something like
def index():
      
    if request.vars != {}:
    
        db.nodeType.insert(value=request.vars.value)
      
        
    rows = db(db.nodeType.value!=None).select()
    
    return dict(types=rows)
    
    
    
def about():

    return dict()    
    
def view():



    if len(request.args) != 0:
        
        typeId = db(db.nodeType.value==request.args[0]).select()
        
        rows = db(db.node.type == typeId[0]).select()
                                  
        
        return dict(page=request.args[0], data=rows)
    else:
        redirect('http://%s/%s/%s/' % (request.env.http_host, request.application, request.controller))

def node():
    # Check if the supplied a node request
    if len(request.args) != 0:
    
        # Search for the node
        current_node = db(db.node.url==request.args[0]).select()
                
        # Check if we got a node
        if len(current_node):
            current_node = current_node[0]
            
            # Get Node Attributes
            attrs = db(db.nodeAttr.nodeId==current_node).select()
        
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
                    
            return dict(node=current_node, node_attributes=attrs, node_list=cat_dict)

        else:
            # Requested node not found in the database.
            raise HTTP(404, "Node not Found")
    else:
        # No node was requested, Redirect to index of current controller
        redirect('http://%s/%s/%s/' % (request.env.http_host, request.application, request.controller))
        
        

def nodeJon():
    if len(request.args) != 0:
        nodeId = db(db.node.url==request.args[0]).select()
                
               
        if len(nodeId) == 0:
            raise HTTP(404, "Node not Found")
            
        else:
            # retreive info on the node and it's linked nodes
            
            category = db(db.nodeType.id!=None).select()
        
            attrs = db(db.nodeAttr.nodeId==nodeId[0]).select()
        
            #grab rows where nodeId == node.id
            links1 = db(db.linkTable.nodeId==nodeId[0].id).select()
            #grab rows where linkId == node.id
            links2 = db(db.linkTable.linkId == nodeId[0].id).select()
        
            links = []
        
            for row in links1:
                
                links.append(row.linkId)
        
            for row in links2:
            
                links.append(row.nodeId)
            
            relatedNodes = {}
            
            rows = db(db.node.id.belongs(links)).select()
                  
            for x in category:
            
                # relatedNodes is a dictionary with nodeType.id as the key, each entry is a
                # list of dictionaries containing info on those nodes
                relatedNodes[x.value] = []   
                              
                for y in rows:                   
                
                    if y.type==x.id:
                    
                        relatedNodes[x.value].append({'id':y.id, 'name':y.name, 'url':y.url, 'pic':'Test'})      
                  
                if len(relatedNodes[x.value])==0:
                        
                    del relatedNodes[x.value]
                    
            return dict(node=nodeId[0], data=attrs, links=links, node_list=relatedNodes)
    else:
        redirect('http://%s/%s/%s/' % (request.env.http_host, request.application, request.controller))

def link():

    # handle database update and redirect
    if(request.vars != {}):
        
        # TODO: Prevent redundant entries     
        db.linkTable.insert(nodeId=int(request.vars.node), linkId=int(request.vars.linkNode))
        
        redirect(URL(request.application, request.controller, "node/%s" % request.vars.url))   

    # handle empty arguments
    if(len(request.args) != 0):
        
        # grab the node with this url
        node = db(db.node.url == request.args[0]).select()
        
    else:
    
        raise HTTP(404, "Node not found")
        
    # Generate a set containing all nodes
    nodeSet = db(db.node.id != None).select()

    return dict( node=node[0], nodeSet=nodeSet )



def edit():

    if(request.vars != {}):
    
        if(request.vars.new == True):
        
            db.node.insert(type=request.vars.nodeType, name=request.vars.name, url=request.vars.url)    
    
        else:
    
            #BAD TODO: RECODE
            db(db.node.id == request.vars.id).update(type=request.vars.nodeType,
                                                     name=request.vars.name,
                                                     url=request.vars.url,
                                                     picURL=request.vars.pic_url,
                                                     description=request.vars.desc
                                                     )
        
            for key,attr in request.vars.items():
        
                if key.startswith('attr.'):
            
                    print 'attr:', key[5:]," val", attr
                
                    #TODO: protect against misc hits
                
                    db(db.nodeAttr.id==key[5:]).update(value=attr)
            
            
            # delete checked attributes
            if request.vars.removeAttr != None:
                
                if len(request.vars.removeAttr) == 1:
                
                    db(db.nodeAttr.id == int(request.vars.removeAttr)).delete()
                
                else:
                    for remAttr in request.vars.removeAttr:
            
                        db(db.nodeAttr.id == int(remAttr)).delete()     
                            
        redirect('http://%s/%s/%s/node/%s' % (request.env.http_host, request.application, request.controller, request.vars.url))

    nodeList = []

    if(len(request.args) != 0):
        node = db(db.node.url == request.args[0]).select()
       
    
        attr = db(db.nodeAttr.nodeId==node[0]).select()
    
        node = node[0]
    
        new = False
        
    else:
        #THIS WILL BREAK HERE AS NODE IS NOT SET
        
        node = None
        
        attr = None
        
        new = True
        
    rows = db(db.nodeType.id != None).select()
    
    vocab = db(db.vocab.id != None).select()
    
    nodeSet = db(db.node.id != None).select()

    return dict( types=rows, node=node, attr=attr, vocab=vocab, new=new, nodeSet=nodeSet )
    
def addCat():
        
    return dict()
    
def addAttr():

    if len(request.vars) != 0:
               
        db.nodeAttr.insert(nodeId=request.vars.nodeId, vocab=request.vars.attr, value="default")
        
               
        redirect('http://%s/%s/%s/edit/%s' % (request.env.http_host, request.application, request.controller, request.vars.nodeUrl))

    node = db(db.node.url == request.args[0]).select()

    attr = db(db.nodeAttr.nodeId == node[0].id).select()

    vocab = db(db.vocab.id != None).select()

    return dict(nodeName=request.args[0], nodeId=node[0].id, attr=attr, vocab=vocab)

def addVocab():

    if len(request.vars) != 0:
    
        db.vocab.insert(value=request.vars.value)
        
        redirect('http://%s/%s/%s/addAttr/%s' % (request.env.http_host, request.application, request.controller, request.vars.nodeUrl))

    vocab = db(db.vocab.id != None).select()

    return dict(nodeUrl=request.args[0], vocab=vocab )
    


def display_form():
   form = SQLFORM(db.node)
   if form.accepts(request.vars, session):
       response.flash = 'form accepted'
   elif form.errors:
       response.flash = 'form has errors'
   else:
       response.flash = 'please fill out the form'
   return dict(form=form)
