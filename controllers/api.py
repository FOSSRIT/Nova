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
        search = (db.node.description.contains(request.vars.search)) |\
                     (db.node.name.contains(request.vars.search)) |\
                     (db.node.url.contains(request.vars.search)) |\
                     (
                         (db.node.id == db.nodeAttr.nodeId) &\
                         (db.nodeAttr.value.contains(request.vars.search))
                     )
    
    # Category Criteria
    if request.vars.category and len(request.vars.category):
        typeId = db(db.nodeType.value==request.vars.category).select().first()
        
        if search:
            search = search & (db.node.type == typeId)
        else:
            search = (db.node.type == typeId)

    # If no criteria, then select everything
    if not search:
        search = (db.node.id>0) 

    return dict(nodes=db(search).select(db.node.id, db.node.name, db.node.url, db.node.description, db.node.picFile, orderby=orderby,limitby=(limit_start,limit_end),groupby=db.node.id).as_list() )
