# coding: utf8
from math import ceil
MAX_PER_PAGE = 12

def index(): 
    redirect(URL('main','node', args="csi"))
    return dict()
def about(): return dict()    

def search():
    """
    A Very basic search system, searches node desc, name and attributes for nodes.
    Doesn't have ranking or duplicate removing at this time.
    """
    master = []
    if request.vars.query:
        # Search node names and descriptions
        results = db( (db.node.description.contains(request.vars.query)) | (db.node.name.contains(request.vars.query))).select()
        
        # Search attributes
        results2 = db(db.nodeAttr.value.contains(request.vars.query)).select(db.nodeAttr.nodeId)
        
        # Combine lists into one list of nodes
        for result in results:
            master.append(result)
            
        for result in results2:
            master.append(result.nodeId)

    return dict(master=master)
    
def category_ajax():
    typeId = db(db.nodeType.value==request.args(0)).select().first()
    rows = db(db.node.type == typeId).select(orderby=~db.node.modified)
    rows_array = []
    for row in rows:
        row_dict = {}
        row_dict['id'] = row.id
        row_dict['name'] = row.name
        row_dict['url'] = row.url
        row_dict['picFile'] = row.picFile
        #row_dict['description'] = row.description
        rows_array.append(row_dict)
    response.view = "generic.json"
    return dict(rows=rows_array)

def category():
    """
    Shows a category of nodes
    Uses request args to determine args (TODO: pages)
    """
    # Check for category name
    if len(request.args):
        
        # Get row that matches category type
        typeId = db(db.nodeType.value==request.args[0]).select().first()
                                  
        return dict(category=typeId)
    else:
        # No category requested
        raise HTTP(404, "Category not specified")

def nodeid():
    try:
        current_node = db(db.node.id==request.args[0]).select().first()
        redirect( URL('node', args=current_node.url) )
    except Exception, oops:
        raise HTTP(404, oops)#"Node not found")


def node():
    # Check if the supplied a node request
    if len(request.args):
    
        # Search for the node
        current_node = db(db.node.url==request.args[0]).select()
                
        # Check if we got a node
        if len(current_node):
            current_node = current_node[0]
            
            # Get Node Attributes
            attrs = db(db.nodeAttr.nodeId==current_node).select(orderby=db.nodeAttr.weight)
        
            # Grab nodes from Linked Table ##
            cat_dict = get_node_links(current_node)
                    
            return dict(node=current_node, node_attributes=attrs, node_list=cat_dict)

        else:
            # Requested node not found in the database.
            raise HTTP(404, "Node not Found")
    else:
        # No node was requested, Redirect to index of current controller
        redirect('http://%s/%s/%s/' % (request.env.http_host, request.application, request.controller))        

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
