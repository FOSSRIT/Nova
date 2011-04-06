# coding: utf8
# try something like
def index():
    response.view = "browse/index.html"
    attr = db(db.vocab.value == request.vars.attribute).select().first()
    
    if attr:
        needs = db((db.nodeAttr.vocab==attr) & (db.node.id == db.nodeAttr.nodeId)).select(
            db.nodeAttr.value,
            db.node.name,
            db.node.url,
            db.node.picFile,
            orderby=~db.node.modified)
    
        return dict(mode_text=attr.value, needs=needs)
    else:
        raise HTTP(404, "Attribte not found")
