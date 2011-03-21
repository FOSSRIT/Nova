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
    return dict(id=entry.id, link=entry.link, tags=entry.tags,
                description=entry.description, title=entry.title,
                feedid=entry.feed)

def edit_entry():
     entry = db(db.rss_entry.id == request.args(0)).select().first()
     
     if not entry:
         raise HTTP(404, "Entry not found")
     
     form = SQLFORM(db.rss_entry, entry, fields=['tags'], showid=False)
     
     if form.accepts(request.vars):
         #ADD TO LOG
         db.syslog.insert(action="Edited Feed Entry", target=entry.id, target2="Tags")
     
         entry = db(db.rss_entry.id == request.args(0)).select().first()
         return SPAN(A('Edit Tags', _href=URL('feeds','edit_entry', args=entry.id, extension="load"), _class="pill button", cid="feed_%s_buttons"%entry.id), tags_2_html(entry.tags))
         
     return dict(form=form)
