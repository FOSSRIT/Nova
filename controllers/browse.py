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
            db.node.tags,
            orderby=~db.node.modified)
    
        return dict(mode_text=attr.value, needs=needs)
    else:
        raise HTTP(404, "Attribte not found")

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
                
        for row in db(db.rss_entry.tags != []).select(db.rss_entry.tags):
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
            if count / 10.0 <= 1:
                size = count / 10.0 + 1
            elif count / 10.0 > 3:
                size = 3
            else:
                size = count / 10.0
            
            ret.append( A("%s (%d)" % (tag, count), _href=URL('browse','tags', args=tag),
                _style="font-size: " + str( size )+ "em;") )
        
        return dict(tagcount=ret)
