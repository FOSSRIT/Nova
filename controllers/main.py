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
        results = db(
                    (db.node.description.contains(request.vars.query)) |
                    (db.node.name.contains(request.vars.query)) |
                    (
                         (db.node.id == db.nodeAttr.nodeId) &
                         (db.nodeAttr.value.contains(request.vars.query))
                     )
                    ).select(db.node.id, db.node.name, db.node.url, groupby=db.node.id)

    return dict(master=results)

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
                 ).select(db.syslog.string_cache, db.syslog.date, orderby=~db.syslog.id)
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


@cache(request.env.path_info,time_expire=60*60,cache_model=cache.disk)
def feed():
    node = get_node_or_404(request.args(0))
    import gluon.contrib.feedparser as feedparser
    
    description = "Feed sources: %s"% (", ".join( node.feeds or [] ))
    entries = []
    
    for feed in (node.feeds or []):
        data = feedparser.parse(feed)
        try:
            entries += [dict(title = entry.title,
              link = entry.link,
              description = entry.description,
              created_on = entry.updated_parsed) for entry in data.entries]
              
        except:
            entries += [dict(title="ERROR IN %s" % feed,
              link = "",
              description = "Error reading feed",
              created_on = request.now)]
    
    local_entries = db(db.blog.nodeId == node.id).select()
    entries += [dict(title = entry.title,
              link = "http://%s%s" % (request.env.http_host, URL('main','blog',args=[node.url, entry.id])),
              description = entry.body,
              created_on = entry.date.timetuple()) for entry in local_entries]
    
    entries = sorted(entries, key=lambda entry: entry['created_on'], reverse=True)
    
    return dict(title=node.name,
                link = URL('main', 'blog', args=node.url),
                description = description,
                created_on = request.now,
                entries = entries)

def blog():
    node = get_node_or_404(request.args(0))
    
    if request.args(1):
        entries = db( (db.blog.nodeId == node.id) & (db.blog.id == request.args(1) ) ).select(orderby=~db.blog.id)
    else:
        entries = db(db.blog.nodeId == node.id).select(orderby=~db.blog.id)
    
    return dict(entries=entries, node=node)

@auth.requires_login()
@auth.requires_membership("Site Admin")
def email():
    node = get_node_or_404(request.args(0))
    links = get_node_links( node )
    
    emails = []
    for link in links['People']:
        emails.append( db(db.auth_user.home_node == link.id).select().first().email)
    
    return dict(emails=emails, node=node)
