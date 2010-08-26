# coding: utf8
from math import ceil
MAX_PER_PAGE = 10

def index(): return dict()
def about(): return dict()    
    
def category():
    """
    Shows a category of nodes
    Uses request args to determine args (TODO: pages)
    """
    # Check for category name
    if len(request.args):
        try:
            page = int(request.args[1])
            if page < 1:
                page = 1
        except:
            page = 1
            
        # Get rows that match category type
        typeId = db(db.nodeType.value==request.args[0]).select()
        rows = db(db.node.type == typeId[0]).select(limitby=((page - 1) * MAX_PER_PAGE, page * MAX_PER_PAGE))
        pages = int(ceil(db(db.node.type == typeId[0]).count()/float(MAX_PER_PAGE)))
                                  
        return dict(page=request.args[0], data=rows, total_pages=pages, page_num=page)
    else:
        # No category requested
        raise HTTP(404, "Category not specified")

def node():
    # Check if the supplied a node request
    if len(request.args):
    
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

def addCat():
        
    return dict()

def display_form():
   form = SQLFORM(db.node)
   if form.accepts(request.vars, session):
       response.flash = 'form accepted'
   elif form.errors:
       response.flash = 'form has errors'
   else:
       response.flash = 'please fill out the form'
   return dict(form=form)
