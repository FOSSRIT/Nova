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
                    "Url": URL('main','node', args=cNode.url, extension="").xml(),
                    "Pic": URL('default','thumb',args=[150,150,cNode.picFile], extension="").xml() \
                           if cNode.picFile else URL('static', 'images', args='placeholder_thumb.png', extension="")
                    }
            tmp_list.append(info)
        h_list.append((highlight.title, tmp_list))
        
    return dict(highlights=h_list)
    
def about(): return dict()

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
        total_tags = 0
        tagcount = {}
        for row in db(db.node.tags != []).select(db.node.tags):
            for tag in row.tags:
                total_tags += 1
                tagcount[tag.lower()] = tagcount.get(tag.lower(), 0) + 1
                
        for row in db(db.blog.tags != []).select(db.blog.tags):
            for tag in row.tags:
                total_tags += 1
                tagcount[tag.lower()] = tagcount.get(tag.lower(), 0) + 1
        
        # Make a sorted list of tuples key, frequency by frequency
        import operator
        sorted_x = sorted(tagcount.iteritems(), key=operator.itemgetter(0))
        #sorted_x.reverse()
        
        # Make html output
        ret = UL(_class='comma-separated')
        for tag, count in sorted_x:
            if count / 10.0 < 1:
                size = count / 10.0 + 1
            elif count / 10.0 > 3:
                size = 3
            else:
                size = count / 10.0
            
            ret.append( A("%s (%d)" % (tag, count), _href=URL('main','tags', args=tag),
                _style="font-size: " + str( size )+ "em;") )
        
        return dict(tagcount=ret)

def _get_feed(feed):
    import gluon.contrib.feedparser as feedparser
    import datetime
    data = feedparser.parse(feed)
    try:
        return [dict(title = "[%s] %s" %(data.feed.title, entry.title),
           link = entry.link,
           description = entry.description,
           #author = "" if not hasattr(entry, "author_detail") else entry.author_detail.name, 
           created_on = datetime.datetime(*entry.updated_parsed[:6])) for entry in data.entries]

    except:
        return [dict(title="ERROR IN %s" % feed,
        link = "",
        description = "Error reading feed",
        created_on = request.now)]

    return entries

def feed():
    node = get_node_or_404(request.args(0))
    
    description = "Feed sources: %s"% (", ".join( node.feeds or [] ))
    entries = []
    
    for feed in (node.feeds or []):
        entries += cache.disk(feed, lambda: _get_feed(feed),time_expire=60*60)
        
    local_entries = db(db.blog.nodeId == node.id).select()
    entries += [dict(title = "[%s] %s" %(node.url, entry.title),
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
        rows = db( (db.blog.nodeId == node.id) & (db.blog.id == request.args(1) ) ).select(orderby=~db.blog.id)
    else:
        rows = db(db.blog.nodeId == node.id).select(orderby=~db.blog.id)
        
    entries = [dict(title = entry.title,
              id = entry.id,
              link = "http://%s%s" % (request.env.http_host, URL('main','blog',args=[node.url, entry.id])),
              description = entry.body,
              author = entry.author,
              tags = entry.tags,
              created_on = entry.date) for entry in rows]
    
    return dict(
            title=node.name,
            link = URL('main', 'blog', args=node.url),
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
