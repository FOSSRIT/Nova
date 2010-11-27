# coding: utf8

def index():
    redirect(URL('main','node', args="csi"))
    #return dict()
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
    if request.args(0):
        typeId = db(db.nodeType.value==request.args(0)).select().first()
        rows = db(db.node.type == typeId).select(orderby=~db.node.modified)
    else:
        #limitby=(0,21)
        rows = db(db.node.id != 0).select(orderby=~db.node.modified)
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

def node_print():
    return node()

def node_activity():
    current_node =  get_node_or_404(request.args(0))
    # Grab Node History
    activity = db( 
                    # Target is always a page
                    (db.syslog.target == current_node.id) | 
                    ( # Grab Target2 if Link and unlink pages
                      (
                        (db.syslog.action == 'Linked Page') |
                        (db.syslog.action == 'Unlinked Page')
                      ) & (db.syslog.target2 == current_node.id)
                    )
                 ).select(db.syslog.string_cache, db.syslog.date)
    return dict(activity=activity,node=current_node)

def log():
    page = 0
    if request.args(0):
        try:
            page = int(request.args(0))
        except:
            pass

    record_start = 100 * page
    return dict(log=db(db.syslog.id>0).select(orderby=~db.syslog.id, limitby=(record_start,record_start+100)),page=page)

@auth.requires_login()
def watched():
    from datetime import datetime, timedelta
    if auth.user.watch_nodes:
        activity = db( 
                    # Target is always a page
                    (db.syslog.target.belongs(auth.user.watch_nodes)) | 
                    ( # Grab Target2 if Link and unlink pages
                      (
                        (db.syslog.action == 'Linked Page') |
                        (db.syslog.action == 'Unlinked Page')
                      ) & (db.syslog.target2.belongs(auth.user.watch_nodes))
                    )
                 ).select(db.syslog.string_cache, db.syslog.date, limitby=(0,100), orderby=~db.syslog.id)
    else:
        activity = []

    return dict(watched=auth.user.watch_nodes, activity=activity)

def tags():
    if request.args(0):
        return dict(tag=request.args(0))    
    else:
        # Builds dict of key to frequency
        tagcount = {}
        for row in db(db.node.tags != []).select(db.node.tags):
            for tag in row.tags:
                tagcount[tag] = tagcount.get(tag, 0) + 1
        
        # Make a sorted list of tuples key, frequency by frequency
        import operator
        sorted_x = sorted(tagcount.iteritems(), key=operator.itemgetter(1))
        sorted_x.reverse()
        
        # Make html output
        ret = UL(_class='comma-separated')
        [ret.append(A("%s (%d)" % (tag, count), _href=URL('main','tags', args=tag))) for tag,count in sorted_x]
        
        return dict(tagcount=ret)
