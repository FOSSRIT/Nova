# coding: utf8

def index():
    #redirect(URL('main','node', args="csi"))
    highlights = db(db.highlights.id>0).select(orderby=db.highlights.weight)
    
    h_list = []
    for highlight in highlights:
        tmp_list = []
        for nodeid in highlight.nodes:
            cNode = db(db.node.id == nodeid).select().first()
            info = {
                    "Name": cNode.name,
                    "Url": URL('main','node', args=cNode.url, extension=""),
                    "Pic": node_pic(cNode, 150, 150, True)
                    }
            tmp_list.append(info)
        h_list.append((highlight, tmp_list))
        
    return dict(highlights=h_list)

def search():
    """
    Search is just a static page that will allow the api to return results.
    """
    return dict()

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

def blogid():
    try:
        current_blog = db(db.blog.id==request.args[0]).select().first()
        #current_node = get_home_from_user(current_blog.author)
        redirect( URL('blog', args=[current_blog.nodeId.url,current_blog.id]) )
    except Exception, oops:
        raise HTTP(404, oops)#"Node not found")


def node():
    # Check if the supplied a node request
    if len(request.args):

        # Search for the node
        current_node = db(db.node.url==request.args[0]).select().first()

        # Check if we got a node
        if current_node:
            addRss("Page Activity", URL('main','node_activity',args=current_node.url, extension="rss"), "An rss feed of page edit activity")
            addRss("Blog", URL('main','blog',args=current_node.url, extension="rss"), "An rss feed of %s's Blog posts" % current_node.name)
            #addRss("s Aggregated Feed", _href=URL('main','feed',args=node.url, extension="rss")) OLD and needs to be re-added

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
    addRss("Page Activity", URL('main','log', extension="rss"), "A sitewide activity log of page edits")
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



def feed():
    node = get_node_or_404(request.args(0))
    
    description = node.name
    entries = []
        
    local_entries = db(db.blog.nodeId == node.id).select()
    entries += [dict(title = entry.title,
              link = "http://%s%s" % (request.env.http_host, URL('main','blog',args=[node.url, entry.id])),
              description = entry.body,
              #author = get_home_from_user(entry.author).name,
              created_on = entry.date) for entry in local_entries]
    
    entries = sorted(entries, key=lambda entry: entry['created_on'], reverse=True)
    
    return dict(title=node.name,
                link = URL('main', 'node', args=node.url),
                description = description,
                created_on = request.now,
                entries = entries)

def blog():
    node = get_node_or_404(request.args(0))
    
    if request.args(1):
        try:
            blogId = int(request.args(1))
        except:
            raise HTTP(404, "Invalid Blog")
            
        rows = db( (db.blog.nodeId == node.id) & (db.blog.id == blogId ) ).select(orderby=~db.blog.id)
    else:
        rows = db(db.blog.nodeId == node.id).select(orderby=~db.blog.id)
        
    entries = [dict(title = entry.title,
              id = entry.id,
              link = "http://%s%s" % (request.env.http_host, URL('main','blog',args=[node.url, entry.id], extension="")),
              description = entry.body,
              author = entry.author,
              tags = entry.tags,
              created_on = entry.date) for entry in rows]
    
    return dict(
            title=node.name,
            link = URL('main', 'blog', args=node.url, extension=""),
            description = "%s's blog" % node.name,
            created_on = request.now,
            entries=entries, node=node)

@auth.requires_login()
@auth.requires_membership("Site Admin")
def email():
    node = get_node_or_404(request.args(0))
    links = get_node_links( node )
    
    emails = []
    for link in links['People']:
        emails.append( db(db.auth_user.home_node == link.id).select().first().email)
    
    return dict(emails=emails, node=node)

def tags():
    # Function Moved, added redirect to prevent broken links
    redirect( URL('browse','tags', args=request.args) )
