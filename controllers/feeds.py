# coding: utf8
# try something like
def index(): 
    feed = db(db.rss_feed.id > 0).select(orderby=db.rss_feed.title)

    return dict(feeds=feed)

def feed():
    feed = db(db.rss_feed.id == request.args(0)).select().first()
    
    if feed:
        entries = feed.rss_entry.select(orderby=~db.rss_entry.updated)

        if request.vars.preview:
            response.view = "feeds/feed_preview.html"
        
        node_owner = db(db.node.feeds.contains(feed.id)).select(db.node.id, db.node.url, db.node.name).first()
        return dict(title=feed.title, created_on=feed.updated,
                link=feed.base_link, rss_link=feed.link, feed_id=feed.id,
                description=feed.description, entries=entries, node_owner=node_owner)
    else:
        session.flash="Feed Not Found"
        redirect( URL('feeds','index') )

def entry():
    entry = db(db.rss_entry.id == request.args(0)).select().first()
    node_owner = db(db.node.feeds.contains(entry.feed.id)).select(db.node.id, db.node.url, db.node.name).first()
    return dict(id=entry.id, link=entry.link, tags=entry.tags,
                description=entry.description, title=entry.title,
                feedid=entry.feed, node_owner=node_owner)

def edit_entry():
     entry = db(db.rss_entry.id == request.args(0)).select().first()
     
     if not entry:
         raise HTTP(404, "Entry not found")
     
     form = SQLFORM(db.rss_entry, entry, fields=['tags'], showid=False)
     
     if form.accepts(request.vars):
         #ADD TO LOG
         node_owner = db(db.node.feeds.contains(entry.feed.id)).select(db.node.id, db.node.url, db.node.name).first()
         db.syslog.insert(action="Edited Feed Entry", target=node_owner, target2=entry.id)
     
         entry = db(db.rss_entry.id == request.args(0)).select().first()
         return SPAN(A('Edit Tags', _href=URL('feeds','edit_entry', args=entry.id, extension="load"), _class="pill button", cid="feed_%s_buttons"%entry.id), tags_2_html(entry.tags))
         
     return dict(form=form)
