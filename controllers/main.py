# coding: utf8
# try something like
def index():
      
    if request.vars != {}:
    
        db.nodeType.insert(value=request.vars.value)
      
        
    rows = db(db.nodeType.value!=None).select()
    
    return dict(types=rows)
    
    
    
def view():



    if len(request.args) != 0:
        
        typeId = db(db.nodeType.value==request.args[0]).select()
        
        rows = db(db.node.type == typeId[0]).select()
                                  
        
        return dict(page=request.args[0], data=rows)
    else:
        redirect('http://%s/%s/%s/' % (request.env.http_host, request.application, request.controller))

def node():
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

def edit():

    print request.vars

    if(request.vars != {}):
    
        if(request.vars.new == True):
        
            db.node.insert(type=request.vars.nodeType, name=request.vars.name, url=request.vars.url)    
    
        else:
    
    
            db(db.node.id == request.vars.id).update(type=request.vars.nodeType)
            db(db.node.id == request.vars.id).update(name=request.vars.name)
            db(db.node.id == request.vars.id).update(url=request.vars.url)
        
            for key,attr in request.vars.items():
        
                if key.startswith('attr.'):
            
                    print 'attr:', key[5:]," val", attr
                
                    #TODO: protect against misc hits
                
                    db(db.nodeAttr.id==key[5:]).update(value=attr)
            
                  
             
        redirect('http://%s/%s/%s/node/%s' % (request.env.http_host, request.application, request.controller, request.vars.url))

    nodeList = []

    if(len(request.args) != 0):
        node = db(db.node.url == request.args[0]).select()
        
        nodeList.append(node[0].id)
        nodeList.append(node[0].type)
        nodeList.append(node[0].name)
        nodeList.append(node[0].url)
    
        attr = db(db.nodeAttr.nodeId==node[0].id).select()
    
        new = False
        
    else:
        nodeList.append('')    
        nodeList.append('')
        nodeList.append('')
        nodeList.append('')
        
        attr = None
        
        new = True
        
    rows = db(db.nodeType.id != None).select()
    
    vocab = db(db.vocab.id != None).select()
    
    return dict( types=rows, node=nodeList, attr=attr, vocab=vocab, new=new )
    
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
