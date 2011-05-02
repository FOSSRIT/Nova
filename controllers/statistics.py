# coding: utf8
# try something like
def index():
    node_count = db(db.node.id>0).count()
    node_type_count = {}
    for ntype in db(db.nodeType.id>0).select():
        node_type_count[ntype.value] = ntype.node.count()
        
    link_count = db(db.linkTable.id>0).count()
    blog_count = db(db.blog.id>0).count()
    feed_count = db(db.rss_feed.id>0).count()
    feed_entry_count = db(db.rss_entry.id>0).count()
    dropbox_count = db(db.filebox.id>0).count()
    dropbox_img_count = db(db.filebox.image == True).count()
    return dict(node_count = node_count, node_type_count=node_type_count,
                link_count=link_count, blog_count=blog_count,
                feed_count=feed_count, feed_entry_count=feed_entry_count,
                dropbox_count=dropbox_count, dropbox_img_count=dropbox_img_count)
