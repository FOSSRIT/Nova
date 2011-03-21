# coding: utf8
db.define_table('rss_feed',
    Field('title', writable=False),
    Field('link', requires=IS_URL()),
    Field('base_link', requires=IS_URL(), writable=False),
    Field('updated','datetime', writable=False),
    Field('description', 'text', writable=False),
    Field('added_on', 'datetime', writable=False, readable=False, default=request.now),
    Field('added_by', db.auth_user, default=auth.user_id,writable=False,readable=False),
    )
    
db.define_table('rss_entry',
    Field('feed', db.rss_feed),
    Field('title'),
    Field('link'),
    Field('updated','datetime'),
    Field('description', 'text'),
    format='%(rss_feed.title)s: %(title)s'
    )

import gluon.contrib.feedparser as feedparser
from time import mktime
from datetime import datetime

def update_feed(feed):
    status_log = ["Checking Feed: %s" % feed.link]
    try:
        d = feedparser.parse( feed.link )
    
        if d.channel.has_key("link"):
            link = d.channel.link
        else:
            for link in d.channel.links:
                if link.rel == "self":
                    link = link.href
                    break
            else:
                link = "#"
            
    
        # Update Feed Data
        feed.update_record(title=d.channel.title,
                           description=d.channel.description if d.channel.has_key("description") and d.channel.description != "" else d.channel.title,
                           updated = request.now,
                           base_link =link)
        
        for entry in d.entries:
            entry_feed = db( (db.rss_entry.link == entry.link) & (db.rss_entry.feed == feed)).select().first()
            
            
            if entry_feed:
                if entry_feed.updated != datetime.fromtimestamp(mktime(entry.updated_parsed)):
                    status_log.append("Updating Entry: %s" % entry.title)
                    entry_feed.update(title=entry.title, description=entry.description or entry.title,
                                      updated = entry.updated_parsed)
            else:
                status_log.append("Adding Entry: %s" % entry.title)
                db.rss_entry.insert(title=entry.title, feed=feed,
                                     link=entry.link, description=entry.description,
                                     updated = datetime.fromtimestamp(mktime(entry.updated_parsed)))
    #except Exception as err:
    #    status_log.append("ERROR: %s" % err)
    except:
        status_log.append("ERROR")
    return status_log

def update_feeds():
    status_log = ["Starting Update Process"]
    
    for feed in db(db.rss_feed.id>0).select():
        status_log += update_feed(feed)
    return status_log
