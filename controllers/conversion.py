# coding: utf8
# try something like
def index(): return dict(message="hello from conversion.py")

def markmin_to_html():
    for record in db(db.node.id>0).select(orderby=db.node.modified):
        record.update_record(description=MARKMIN(record.description).xml())
    
    for record in db(db.nodeAttr.id>0).select(orderby=db.nodeAttr.modified):
        record.update_record(value=MARKMIN(record.value).xml())
