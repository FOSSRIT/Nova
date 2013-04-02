# coding: utf8


def log_to_string(entry, links=True):
    user = db(db.auth_user.id==entry.user).select(db.auth_user.home_node).first()
    home_node = db(db.node.id==user.home_node).select().first()
    
    def link_page(entry):
        page = db(db.node.id==entry.target).select().first()
        page2 = db(db.node.id==entry.target2).select().first()
        
        if page and page2:
            return "linked <a href=\"%s\">%s</a> to <a href=\"%s\">%s</a>." % (
                    URL('main','node',args=page.url, extension=""),
                    page.name,
                    URL('main','node',args=page2.url, extension=""),
                    page2.name
                )
        else:
            if page2:
               page = page2
               
            return "linked <a href=\"%s\">%s</a> to a page that no longer exists." % (
                    URL('main','node',args=page.url, extension=""),
                    page.name
                )
    
    def unlink_page(entry):
        page = db(db.node.id==entry.target).select().first()
        page2 = db(db.node.id==entry.target2).select().first()
        
        if page and page2:
        
            return "unlinked <a href=\"%s\">%s</a> from <a href=\"%s\">%s</a>." % (
                    URL('main','node',args=page.url, extension=""),
                    page.name,
                    URL('main','node',args=page2.url, extension=""),
                    page2.name
                )
        else:
            if page2:
               page = page2
               
            return "unlinked <a href=\"%s\">%s</a> from a page that no longer exists." % (
                    URL('main','node',args=page.url, extension=""),
                    page.name
                )
    
    def add_page(entry):
        page = db(db.node.id==entry.target).select().first()
        
        if page:
            return "created a new page entitled <a href=\"%s\">%s</a>." % (URL('main','node',args=page.url, extension=""), page.name)
        else:
            return "created a new page that no longer exists"
            
    def edit_page(entry):
        page = db(db.node.id==entry.target).select().first()
    
        if page:
            return "edited <a href=\"%s\">%s</a>'s %s" % (
                URL('main','node',args=page.url, extension=""),
                page.name,
                entry.target2
            )
        else:
            return "edited a page that no longer exists"
            
    def delete_page(entry):
        return "deleted a page"
        
    def add_attribute(entry):
        page = db(db.node.id==entry.target).select().first()
        
        if page:
            attribute = db(db.nodeAttr.id==entry.target2).select().first()
            if attribute:
                return "Added %s attribute to <a href=\"%s\">%s</a>." % (
                        attribute.vocab.value,
                        URL('main','node',args=page.url, extension=""),
                        page.name
                    )
            else:
                return "Added an attribute that no longer exists to <a href=\"%s\">%s</a>." % (
                        URL('main','node',args=page.url, extension=""),
                        page.name
                    )
        else:
            return "Added an attribute to a page that no longer exists."
    
        
    def edit_attribute(entry):
        page = db(db.node.id==entry.target).select().first()
        
        if page:
            attribute = db(db.nodeAttr.id==entry.target2).select().first()
            if attribute:
                return "Edited %s attribute of <a href=\"%s\">%s</a>." % (
                        attribute.vocab.value,
                        URL('main','node',args=page.url, extension=""),
                        page.name
                    )
            else:
                return "Edited an attribute that no longer exists of <a href=\"%s\">%s</a>." % (
                        URL('main','node',args=page.url, extension=""),
                        page.name
                    )
        else:
            return "Edited an attribute to a page that no longer exists."
    
    def del_attriubte(entry):
        page = db(db.node.id==entry.target).select().first()
        
        if page:
            attribute = db(db.nodeAttr.id==entry.target2).select().first()
            return "Deleted an attribute from <a href=\"%s\">%s</a>." % (
                        URL('main','node',args=page.url, extension=""),
                        page.name
                    )
        else:
            return "Deleted an attribute from a page that no longer exists."



    def add_blog(entry):
        node = db(db.node.id==entry.target).select().first()
        entry = db(db.blog.id==entry.target2).select().first()
        
        if entry:
            return "created a new blog post entitled <a href=\"%s\">%s</a>." % (URL('main','blog',args=[node.url, entry.id], extension=""), entry.title)
        else:
            return "created a new blog post that no longer exists"
            
    def edit_blog(entry):
        node = db(db.node.id==entry.target).select().first()
        entry = db(db.blog.id==entry.target2).select().first()
        
        if entry:
            return "edited a blog post entitled <a href=\"%s\">%s</a>." % (URL('main','blog',args=[node.url, entry.id], extension=""), entry.title)
        else:
            return "edited a blog post that no longer exists"
            
    def edit_feed(entry):
        node = db(db.node.id==entry.target).select().first()
        rssent = db(db.rss_entry.id==entry.target2).select().first()
        
        if rssent:
            return "edited one of <a href=\"%s\">%s</a>'s feed post entitled <a href=\"%s\">%s</a>." % \
                (
                    URL('main','node',args=node.url, extension=""),
                    node.name,
                    URL('feeds','entry',args=rssent.id, extension=""),
                    rssent.title or "No Title"
                )
        else:
            return "edited a feed post that no longer exists"
            
    def delete_blog(entry):
        node = db(db.node.id==entry.target).select().first()
        entry = db(db.blog.id==entry.target2).select().first()
        
        if entry:
            return "deleted a blog post entitled %s." % (entry.title)
        else:
            return "deleted a new blog post that no longer exists, WHAT?"
            
    def add_ref_by_page(entry):
        node = db(db.node.id==entry.target).select().first()
        node2 = db(db.node.id==entry.target2).select().first()
        
        #todo add if entry check
        return "added <a href=\"%s\">%s</a>'s page tag (%s) to <a href=\"%s\">%s</a>." % \
                    (
                    URL('main','node',args=node.url, extension=""), node.name,
                    node.url,
                    URL('main','node',args=node2.url, extension=""), node2.name
                     )
            
    def rem_ref_by_page(entry):
        node = db(db.node.id==entry.target).select().first()
        node2 = db(db.node.id==entry.target2).select().first()
        
        #todo add if entry check
        return "removed <a href=\"%s\">%s</a>'s page tag  (%s) form <a href=\"%s\">%s</a>." % \
                    (URL('main','node',args=node.url, extension=""), node.name,
                     node.url,
                     URL('main','node',args=node2.url, extension=""), node2.name)
                     
    def add_ref_by_blog(entry):
        node = db(db.node.id==entry.target).select().first()
        entry = db(db.blog.id==entry.target2).select().first()
        
        #todo add if entry check
        return "added <a href=\"%s\">%s</a>'s page tag (%s) to <a href=\"%s\">%s</a>." % \
                    (
                    URL('main','node',args=node.url, extension=""), node.name,
                    node.url,
                    URL('main','blogid',args=entry.id, extension=""), entry.title
                     )
            
    def rem_ref_by_blog(entry):
        node = db(db.node.id==entry.target).select().first()
        entry = db(db.blog.id==entry.target2).select().first()
        
        #todo add if entry check
        return "removed <a href=\"%s\">%s</a>'s page tag  (%s) form <a href=\"%s\">%s</a>." % \
                    (
                    URL('main','node',args=node.url, extension=""), node.name,
                    node.url,
                    URL('main','blogid',args=entry.id, extension=""), entry.title
                    )
                    
    def add_ref_by_feed(entry):
        node = db(db.node.id==entry.target).select().first()
        entry = db(db.rss_entry.id==entry.target2).select().first()
        
        #todo add if entry check
        return "added <a href=\"%s\">%s</a>'s page tag (%s) to <a href=\"%s\">%s</a>." % \
                    (
                    URL('main','node',args=node.url, extension=""), node.name,
                    node.url,
                    URL('feeds','entry',args=entry.id, extension=""), entry.title
                     )
            
    def rem_ref_by_feed(entry):
        node = db(db.node.id==entry.target).select().first()
        entry = db(db.rss_entry.id==entry.target2).select().first()
        
        #todo add if entry check
        return "removed <a href=\"%s\">%s</a>'s page tag  (%s) form <a href=\"%s\">%s</a>." % \
                    (
                    URL('main','node',args=node.url, extension=""), node.name,
                    node.url,
                    URL('feeds','entry',args=entry.id, extension=""), entry.title
                    )
    
    def add_match(entry):
        node = db(db.node.id==entry.target).select().first()
        entry = db(db.matchingAttribute.id==entry.target2).select().first()
        
        return "Added <a href=\"%s\">%s</a> to <a href=\"%s\">%s</a>'s list of %s <a href=\"%s\">%s</a>." % \
             (
                 URL('match', 'browse', args=[entry.category.namePlural, entry.value], extension=""), entry.value,
                 URL('main','node',args=node.url, extension=""), node.name,
                 "" if entry.provides else "desired",
                 URL('match', 'browse', args=[entry.category.namePlural], extension=""), entry.category.namePlural
              )
        
    def rem_match(entry):
        node = db(db.node.id==entry.target).select().first()
        entry = db(db.matchingAttribute_archive.current_record==entry.target2).select(orderby=~db.matchingAttribute_archive.id).first()
        
        return "Removed <a href=\"%s\">%s</a> from <a href=\"%s\">%s</a>'s list of %s <a href=\"%s\">%s</a>." % \
             (
                 URL('match', 'browse', args=[entry.category.namePlural, entry.value], extension=""), entry.value,
                 URL('main','node',args=node.url, extension=""), node.name,
                 "" if entry.provides else "desired",
                 URL('match', 'browse', args=[entry.category.namePlural], extension=""), entry.category.namePlural
              )
     
    def edit_match(entry):
        node = db(db.node.id==entry.target).select().first()
        entry = db(db.matchingAttribute.id==entry.target2).select().first()
        
        return "Edited <a href=\"%s\">%s</a> on <a href=\"%s\">%s</a>'s list of %s <a href=\"%s\">%s</a>." % \
             (
                 URL('match', 'browse', args=[entry.category.namePlural, entry.value], extension=""), entry.value,
                 URL('main','node',args=node.url, extension=""), node.name,
                 "" if entry.provides else "desired",
                 URL('match', 'browse', args=[entry.category.namePlural], extension=""), entry.category.namePlural
              )
              
    switch = {
        "Linked Page":link_page,
        "Unlinked Page":unlink_page,
        "Added Page":add_page,
        "Edited Page":edit_page,
        "Deleted Page":delete_page,
        "Added Attribute":add_attribute,
        "Edited Attribute":edit_attribute,
        "Deleted Attribute":del_attriubte,
        "Added Blog Entry":add_blog,
        "Edited Blog Entry":edit_blog,
        "Deleted Blog Entry":delete_blog,
        "Edited Feed Entry":edit_feed,
        "Refereced by Page":add_ref_by_page,
        "Derefereced by Page":rem_ref_by_page,
        "Refereced by Blog":add_ref_by_blog,
        "Derefereced by Blog":rem_ref_by_blog,
        "Refereced by Feed":add_ref_by_feed,
        "Derefereced by Feed":rem_ref_by_feed,
        "Added Match Element":add_match,
        "Removed Match Element":rem_match,
        "Edited Match Element":edit_match,
        }
    
    ret_val = "%s | <a href=\"%s\">%s</a> %s" % (
            entry.date.strftime(DATE_FORMAT),
            URL('main','node',args=home_node.url, extension=""),
            home_node.name,
            switch[entry.action](entry)
        )
        
    if links:
        return ret_val
    else:
        return TAG(ret_val).flatten()
        
def log_str_auto_compute(record):
    if not record.has_key('user'):
        record['user'] = auth.user_id
    if not record.has_key('date'):
        record['date'] = request.now
    class DictObj(dict):
        def __getattr__(self, name):
            #try:
            return self.__getitem__(name)
            #except KeyError:
            #    return super(DictObj,self).__getattr__(name)

    msg = log_to_string(DictObj(record))

    return msg
    
db.define_table('syslog',
    Field('date', 'datetime', writable=False, readable=False, default=request.now),
    Field('user','integer', default=auth.user_id,update=auth.user_id,writable=False, readable=False),
    Field('action', requires=IS_IN_SET(
            (
                'Linked Page',
                'Unlinked Page',
                'Added Page',
                'Edited Page',
                'Deleted Page',
                'Added Attribute',
                'Edited Attribute',
                'Deleted Attribute',
                'Added Blog Entry',
                'Edited Blog Entry',
                'Deleted Blog Entry'
                'Edited Feed Entry',
                'Refereced by Page',
                'Derefereced by Page',
                'Refereced by Blog',
                'Derefereced by Blog',
                'Added Match Element',
                'Removed Match Element',
                'Edited Match Element',
            )
        ) ),
    Field('target', 'integer'),
    Field('target2'),
    Field('additional'),
    Field('string_cache', compute=log_str_auto_compute),
    )
