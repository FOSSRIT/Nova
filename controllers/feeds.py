# coding: utf8
# try something like
def index(): 
    feed = db(db.rss_feed.id > 0).select(orderby=db.rss_feed.title)

    return dict(feeds=feed)

def feed():
    try:
        feed_id = int(request.args(0))
    except:
        session.flash="Invalid Feed"
        redirect( URL('feeds','index') )

        
    feed = db(db.rss_feed.id == feed_id).select().first()
    
    if feed:
        if request.vars.preview:
            response.view = "feeds/feed_preview.html"
            entries = feed.rss_entry.select(orderby=~db.rss_entry.updated, limitby=(0,15))
        else:
            entries = feed.rss_entry.select(orderby=~db.rss_entry.updated)
        
        node_owner = db(db.node.feeds.contains(feed.id)).select(db.node.id, db.node.url, db.node.name).first()
        return dict(title=feed.title, created_on=feed.updated,
                link=feed.base_link, rss_link=feed.link, feed_id=feed.id,
                description=feed.description, entries=entries, node_owner=node_owner)
    else:
        session.flash="Feed Not Found"
        redirect( URL('feeds','index') )

def entry():
    try:
        entry_id = int(request.args(0))
    except:
        raise HTTP(404, "Invalid Entry Id")

    entry = db(db.rss_entry.id == entry_id).select().first()
    if entry:
        node_owner = db(db.node.feeds.contains(entry.feed.id)).select(db.node.id, db.node.url, db.node.name).first()
        return dict(id=entry.id, link=entry.link, tags=entry.tags,
                    description=entry.description, title=entry.title,
                    feedid=entry.feed, node_owner=node_owner)
    else:
        session.flash="Entry Not Found"
        redirect( URL('feeds','index') )

def edit_entry():
     entry = db(db.rss_entry.id == request.args(0)).select().first()
     
     if not entry:
         raise HTTP(404, "Entry not found")
     
     form = SQLFORM(db.rss_entry, entry, fields=['tags'], showid=False)
     
     if form.accepts(request.vars):
         #ADD TO LOG
         node_owner = db(db.node.feeds.contains(entry.feed.id)).select(db.node.id, db.node.url, db.node.name).first()
         db.syslog.insert(action="Edited Feed Entry", target=node_owner, target2=entry.id)

         feed_ref_support(request.vars.tags, entry.tags, entry.id)

         entry = db(db.rss_entry.id == request.args(0)).select().first()
         return SPAN(A('Edit Tags', _href=URL('feeds','edit_entry', args=entry.id, extension="load"), _class="pill button", cid="feed_%s_buttons"%entry.id), tags_2_html(entry.tags))
         
     return dict(form=form)
