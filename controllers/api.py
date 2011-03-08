# coding: utf8
# try something like

API_MAX_NODES_PER_PAGE = 50



def index(): return dict(message="hello from api.py")

def search():
    """
    
    Exposes:
        /api/search/
        page       page
        order      Any db.node table
        sort       desc (otherwise asc)
        search     search string
        category   Category name to filter by
        tag        tag filter
        
    """
    # Determine Page Information
    try:
        page = int(request.vars.page) - 1
        if page < 0:
            page = 0
    except:
        page = 0
     
    limit_start = page * API_MAX_NODES_PER_PAGE
    limit_end = (page + 1) * API_MAX_NODES_PER_PAGE
    
    # Determine order information
    try:
        orderby = db.node[request.vars.order]
        if request.vars.sort == 'desc':
            orderby = ~orderby
    except:
        orderby = db.node.name
    
    search = None
    # Search Criteria
    if request.vars.search and len(request.vars.search):
        search = (db.node.description.contains(request.vars.search)) | \
                 (db.node.name.contains(request.vars.search)) | \
                 (db.node.url.contains(request.vars.search)) |\
                 (db.node.tags.contains(request.vars.search))
                 
        # Should we search the attributes table (slow)
        if request.vars.fulltext:
            search = search | (
                         (db.node.id == db.nodeAttr.nodeId) & \
                         (db.nodeAttr.value.contains(request.vars.search))
                      )
    
    # Category Criteria
    if request.vars.category and len(request.vars.category):
        typeId = db(db.nodeType.value==request.vars.category).select().first()
        
        if search:
            search = search & (db.node.type == typeId)
        else:
            search = (db.node.type == typeId)
            
    # Tag Criteria
    if request.vars.tag and len(request.vars.tag):
        if search:
            search = search & (db.node.tags.contains(request.vars.tag))
        else:
            search = (db.node.tags.contains(request.vars.tag))

    # If no criteria, then select everything
    if not search:
        search = (db.node.id>0) 

    return dict(nodes=db(search).select(db.node.id, db.node.name, db.node.url, db.node.description, db.node.picFile, db.node.tags, orderby=orderby,limitby=(limit_start,limit_end),groupby=db.node.id).as_list() )
    
def searchBlog():
    # Determine Page Information
    try:
        page = int(request.vars.page) - 1
        if page < 0:
            page = 0
    except:
        page = 0
     
    limit_start = page * API_MAX_NODES_PER_PAGE
    limit_end = (page + 1) * API_MAX_NODES_PER_PAGE
    
    # Determine order information
    try:
        if request.vars.order=="name":
            request.vars.order = "title"
        orderby = db.blog[request.vars.order]
        if request.vars.sort == 'desc':
            orderby = ~orderby
    except:
        orderby = db.blog.title
    
    search = None
    # Search Criteria
    if request.vars.search and len(request.vars.search):
        search = (db.blog.body.contains(request.vars.search)) | \
                 (db.blog.title.contains(request.vars.search)) | \
                 (db.blog.tags.contains(request.vars.search))
                 
            
    # Tag Criteria
    if request.vars.tag and len(request.vars.tag):
        if search:
            search = search & (db.blog.tags.contains(request.vars.tag))
        else:
            search = (db.blog.tags.contains(request.vars.tag))

    # If no criteria, then select everything
    if not search:
        search = (db.blog.id>0) 

    return dict(blogentries=db(search).select(db.blog.id, db.blog.title, db.blog.body, db.blog.date, db.blog.tags, orderby=orderby,limitby=(limit_start,limit_end),groupby=db.blog.id).as_list() )
    
def links():
    node = get_node_or_404(request.args(0))
    
    retDict = {}
    for key,lst in get_node_links(node).items():
        retDict[key] = []
        for node_id in lst:
            #TODO CONVERT ID TO DICT
            #description=node_id.description,
            retDict[key].append(dict( id=node_id.id, name=node_id.name, url=node_id.url,  picFile=node_id.picFile, tags=node_id.tags ))
    return retDict

@auth.requires_login()
def myFileList():
    return dict(files=db(db.filebox.owner == auth.user_id).select())
    
@auth.requires_login()
def quota():
    return dict( quota=get_quota_usage(), quota_text = get_quota_string(), quota_max=get_quota_usage()>MAX_FILE_STORE)
