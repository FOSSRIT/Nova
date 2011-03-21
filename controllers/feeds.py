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

        return dict(title=feed.title, created_on=feed.updated,
                link=feed.base_link, rss_link=feed.link, feed_id=feed.id,
                description=feed.description, entries=entries)
    else:
        session.flash="Feed Not Found"
        redirect( URL('feeds','index') )

def entry():
    entry = db(db.rss_entry.id == request.args(0)).select().first()
    return dict(id=entry.id, link=entry.link,
                description=entry.description, title=entry.title,
                feedid=entry.feed)
