# coding: utf8
# try something like
def index():
    redirect(URL("browse", "attributes"))

def attributes():
    
    if request.args(0):
        attr = db(db.vocab.value == request.args(0).replace("_", " ")).select().first()
        attrs = db((db.nodeAttr.vocab==attr) & (db.node.id == db.nodeAttr.nodeId)).select(
            db.nodeAttr.value,
            db.node.name,
            db.node.url,
            db.node.picFile,
            db.node.type,
            db.node.tags,
            orderby=~db.node.modified)
    
        return dict(mode_text=request.args(0), attrs=attrs)
    else:
        count = db.nodeAttr.id.count()
        attrList = db((db.vocab.id > 1) & (db.vocab.id == db.nodeAttr.vocab)).select(
            db.vocab.ALL, count, orderby=db.vocab.value, groupby=db.vocab.id)
        
        

        return dict(attributes=[{"value":row.vocab.value, "count":row[count]} for row in attrList])
        
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
            
            if count > 1 or request.vars.showall:
                ret.append( A("%s (%d)" % (tag, count), _href=URL('browse','tags', args=tag),
                    _style="font-size: " + str( size )+ "em; text-decoration: none;") )
            
        return dict(tagcount=ret)
