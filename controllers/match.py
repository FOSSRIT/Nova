# coding: utf8
# try something like
def index():
    return dict(message="Welcome to matchmaking!")
    
def browse():
    if request.args(0):
    
        nodeCategory = db(db.matchingCategory.namePlural == request.args(0)).select().first()
        
        if request.args(1):
            matchedNodes = db(
                (db.matchingAttribute.category==nodeCategory) &
                (db.matchingAttribute.value == request.args(1).replace("_", " ")) &
                (db.node.id == db.matchingAttribute.node)
                ).select(db.matchingAttribute.ALL, db.node.name, db.node.url, db.node.picFile).as_list()
            return dict(category=nodeCategory.as_dict(), matchedNodes=matchedNodes)
        else:
            count = db.matchingAttribute.value.count()
            categoryValues = [{'value':x.matchingAttribute.value, 'count':x[count]} \
                    for x in nodeCategory.matchingAttribute.select(db.matchingAttribute.value, count, groupby=db.matchingAttribute.value)]
        
            return dict(category=nodeCategory.as_dict(), categoryValues=categoryValues)

    else:
        return dict(categories=db(db.matchingCategory.id>0).select(orderby=db.matchingCategory.namePlural).as_list())
        
@auth.requires_login()
def addAttribute():
    if len(request.args) != 3 and len(request.args) != 4:
        raise HTTP(404, "Unexpected Request")
        
    nodeCategory = db(db.matchingCategory.name == request.args(0)).select().first()
    if not nodeCategory:
        raise HTTP(404, "Category Not Found")
    
    node = get_node_or_404(request.args(1))
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node's Attributes")
        
    if "provides" == request.args(2):
        provides = True
    elif "wants" == request.args(2):
        provides = False
    else:
        raise HTTP(404, "Unknown mode")
    
    db.matchingAttribute.value.widget = SQLFORM.widgets.autocomplete(
        request, db.matchingAttribute.value,limitby=(0,10), min_length=2,
        db=db(db.matchingAttribute.category==nodeCategory), keyword="w2p_autocomplete_matchingattr", distinct=True)
    
    submit_str = "Add Desired %s" if request.args(2) == "wants" else "Add %s"
    
    db.matchingAttribute.value.label = nodeCategory.name
    
    if request.args(3):
        attrMatch = db(
            (db.matchingAttribute.category==nodeCategory) &
            (db.matchingAttribute.node == node) &
            (db.matchingAttribute.provides == provides) &
            (db.matchingAttribute.value == request.args(3).replace("_", " "))).select().first()
            
        submit_str = "Edit Desired %s" if request.args(2) == "wants" else "Edit %s"
        if not attrMatch:
            raise HTTP(404, "Attribute Not Found")
    else:
        attrMatch = None
        
    form = SQLFORM(db.matchingAttribute, attrMatch, showid = False, submit_button=submit_str % nodeCategory.name, deletable=True)
    
    
    form.vars.category = nodeCategory
    form.vars.node = node
    form.vars.provides = provides
    

    if form.accepts(request.vars, session):
        #db.syslog.insert(action="Edited Attribute", target=node.id, target2=attr.id)
        return LOAD("match","viewNode",args=[node.url])

        
    return dict(node=node.as_dict(), category=nodeCategory.as_dict(), form=form)
    
def viewNode():
    node = get_node_or_404(request.args(0))
    
    match = []
    for category in db(db.matchingCategory.id>0).select():
        match.append(
            {"category":category,
            "provides":db((db.matchingAttribute.category==category) &
                (db.matchingAttribute.node==node)&(db.matchingAttribute.provides==True)).select(db.matchingAttribute.value, db.matchingAttribute.description).as_list(),
            "wants":db((db.matchingAttribute.category==category) &
                (db.matchingAttribute.node==node)&(db.matchingAttribute.provides==False)).select().as_list(),
            })
        
    return dict(match=match, node=node.as_dict(), can_edit=can_edit(node))

def findMatch():
    if len(request.args) != 2:
        raise HTTP(404, "Unexpected Request")
        
    nodeCategory = db(db.matchingCategory.namePlural == request.args(0)).select(
        db.matchingCategory.id,db.matchingCategory.name,db.matchingCategory.namePlural).first()
    if not nodeCategory:
        raise HTTP(404, "Category Not Found")
    
    node = get_node_or_404(request.args(1))
    
    attrs = db((db.matchingAttribute.category == nodeCategory) & (db.matchingAttribute.node == node)).select()
    
    skillsIOffer = []
    skillsIWant = []
    for attr in attrs:
        if attr.provides:
            skillsIOffer.append(attr.value)
        else:
            skillsIWant.append(attr.value)

    imLookingFor = {}
    skillsIWantCount = len(skillsIWant)
    for match in db((db.matchingAttribute.category == nodeCategory) &
            (db.matchingAttribute.value.belongs(skillsIWant)) &
            (db.matchingAttribute.provides == True)).select():
        
        if match.node.id in imLookingFor:
            imLookingFor[match.node.id]["attrs"].append({"name":match.value, "description":match.description})
        else:
            ct = db((db.matchingAttribute.node==match.node)&
                (db.matchingAttribute.category == nodeCategory) &
                (db.matchingAttribute.value.belongs(skillsIWant)) &
                (db.matchingAttribute.provides == True)).count()
            imLookingFor[match.node.id] = {
                "node":match.node,
                "match":(float(ct)/skillsIWantCount)*100,
                "matchCt": ct,
                "totalCt": skillsIWantCount,
                "attrs":[{"name":match.value, "description":match.description}]}
        
        
    lookingForMe = {}
    for match in db((db.matchingAttribute.category == nodeCategory) &
            (db.matchingAttribute.value.belongs(skillsIOffer)) &
            (db.matchingAttribute.provides == False)).select():
            
        ctTotal = db((db.matchingAttribute.node==match.node)&
                    (db.matchingAttribute.category == nodeCategory) &
                    (db.matchingAttribute.provides == False)).count()
        ctLessMatch = db((db.matchingAttribute.node==match.node)&
                    (db.matchingAttribute.category == nodeCategory) &
                    ~(db.matchingAttribute.value.belongs(skillsIOffer)) &
                    (db.matchingAttribute.provides == False)).count()  
                
        
        if match.node.id in lookingForMe :
            lookingForMe[match.node.id]["attrs"].append({"name":match.value, "description":match.description})
        else:
            lookingForMe[match.node.id] = {
                "node":match.node,
                "match":min((float(ctTotal - ctLessMatch)/ctTotal)*100, 100.0),
                "matchCt": ctTotal - ctLessMatch,
                "totalCt": ctTotal,
                "attrs":[{"name":match.value, "description":match.description}]}

    return dict(node=node,category=nodeCategory.as_dict(),imLookingFor=imLookingFor, lookingForMe=lookingForMe )
