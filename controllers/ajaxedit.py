# coding: utf8

@auth.requires_login()
def editattribute():
    """
    Allows users to edit attributes connected to a node.
    
    Exposes: /ajaxedit/editattribute/NODE_URL_ID/attr_ATTRIBUTE_ID
    """
    # Find the node we are trying to update
    node = get_node_or_404( request.args(0) )
        
    # Check node permissions
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node's Attributes")
    
    # Get attribute we are trying to update
    attr = get_attribute_or_404(node, request.args(1)[5:] )
        
    form = SQLFORM( db.nodeAttr, attr, showid = False,
                    comments=False, fields=['value'],#,'weight'],
                    labels={'value':""}, submit_button="Save",
                    _action = URL('ajaxedit','editattribute',
                    args=[node.url,request.args[1]]))

    if form.accepts(request.vars, session):
        response.view = "generic.load"
        db.syslog.insert(action="Edited Attribute", target=node.id, target2=attr.id)
        
        attr = db(db.nodeAttr.id == attr ).select().first()
        
        return dict(t=XML(attr.value,True, ALLOWED_HTML_TAGS, ALLOWED_HTML_ATTR))

    else:
        response.view = "generic.load"
        return dict(form=form)
        
@auth.requires_login()
def deleteattribute():
    """
    Allows users to delete attributes connected to a node.
    
    Exposes: /ajaxedit/deleteattribute/NODE_URL_ID/attrdel_ATTRIBUTE_ID
    """
    # Find the node we are trying to update
    node = get_node_or_404( request.args(0) )
        
    # Check node permissions
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node's Attributes")
    
    # Get attribute we are trying to delete and delete it
    attr = get_attribute_or_404(node, request.args(1)[8:] )
    db(db.nodeAttr.id==attr).delete()
    db.syslog.insert(action="Deleted Attribute", target=node.id, target2=attr.id)
    
    # A small Cleanup Routine, check if attriubte is
    # still in use, if not delete the attribute
    if db(db.nodeAttr.vocab==attr.vocab).count() == 0:
        db(db.vocab.id==attr.vocab.id).delete()
    
    # Return html attribute list
    response.view = "htmlblocks/attributes.html"
    attr_list = db(db.nodeAttr.nodeId==node).select(orderby=db.nodeAttr.weight)
    return dict(node_attributes=attr_list)

@auth.requires_login()
def addattribute():
    # Find the node we are trying to update
    node = get_node_or_404( request.args(0) )
    
    # Check node permissions
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node's Attributes")
        
    attribute_form = SQLFORM(db.nodeAttr,submit_button="Save",_action = URL('ajaxedit','addattribute', args=[node.url]), comments=False)
    attribute_form.vars.nodeId = node
    
    # If they entered custom text, it will have vocab as '' and the auto complete will not be empty
    if( request.vars.vocab == '' and request.vars._autocomplete_value_aux != '' ):
        # TODO Check content is valid
        request.vars.vocab = db.vocab.insert(value=request.vars._autocomplete_value_aux)
        attribute_form.vars.vocab = request.vars.vocab
            
    if attribute_form.accepts(request.vars, dbio=False):
        a_id = db.nodeAttr.insert(**db.nodeAttr._filter_fields(attribute_form.vars))
        response.view = "htmlblocks/attributes.html"
        attr = db(db.nodeAttr.nodeId==node).select(orderby=db.nodeAttr.weight)
        db.syslog.insert(action="Added Attribute", target=node.id, target2=a_id)
        return dict(node_attributes=attr)
    else:
        attrlist = db(db.vocab.id>0).select(orderby=db.vocab.value)
    
        response.view = "htmlblocks/attribute_inplace_form.html"
        return dict(form=attribute_form,attrlist=attrlist)

@auth.requires_login()
def editnode():
    response.view = "generic.load"
    
    # Find the node we are trying to update
    node = get_node_or_404( request.args(0) )
    
    # Check node permissions
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node")
        
        
    if request.args(1) == "feeds":    
        form = SQLFORM( db.rss_feed, fields=['link'], submit_button="Add Feed",
                        _action = URL('ajaxedit','editnode', args=[node.url,request.args(1)]) )
        
        if form.accepts(request.vars, dbio=False):
            a_id = db.rss_feed.insert(**db.rss_feed._filter_fields(form.vars))
            
            # Add to node
            feeds = node.feeds or []
            feeds += [a_id]
            
            node.update_record(feeds = feeds)
            
            db.syslog.insert(action="Edited Page", target=node.id, target2="Feed")
            
            # Trigger Update
            update_feed(db.rss_feed[a_id])
            
            # Return Feed List
            return "Refresh to view new content"
        
        entry_list = []
        for id in node.feeds or []:
            entry = db(db.rss_feed.id == id).select().first()
            entry_list.append( LI("%s (%s) " % (entry.title, entry.link), A('Remove Feed',_href=URL('ajaxedit','delfeed',args=[node.url,entry.id]))))
            
        return dict(form=DIV(H2("Add Feed"),form,H2("Remove Feed"),UL(entry_list)))
        
        
    form = SQLFORM( db.node, node, fields=[request.args(1)], labels={request.args(1):""},
                    comments=(request.args(1) in ['feeds']), formstyle="divs" , showid = False, submit_button="Save",
                    _action = URL('ajaxedit','editnode', args=[node.url,request.args(1)]) )
                    
    
    if form.accepts(request.vars):
        db.syslog.insert(action="Edited Page", target=node.id, target2=request.args(1))
        if request.args(1) =='tags':

            # Reference Support
            page_ref_support(request.vars.tags, node.tags, node.id)

            return tags_2_html(request.vars.tags)
        else:
            # Grab the new version of the node to populate data
            node = db(db.node.url == request.args(0)).select().first()
            return dict(node=XML(node.get(request.args(1)),True, ALLOWED_HTML_TAGS, ALLOWED_HTML_ATTR))
    else:
        return dict(form=form)
        
@auth.requires_login()
def delfeed():
    # Find the node we are trying to update
    node = get_node_or_404( request.args(0) )
    
    # Check node permissions
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node")
        
    if request.args(1) in node.feeds:
        node.feeds.remove( request.args(1) )
        node.update_record(feeds = node.feeds)
        
        db(db.rss_feed.id == request.args(1)).delete()
        db.syslog.insert(action="Edited Page", target=node.id, target2="Feed")
    redirect(URL("main", "node", args=node.url))
        
@auth.requires_login()
def editphoto():
    # Find the node we are trying to update
    node = get_node_or_404( request.args(0) )
    
    # Check node permissions
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node")
        
        
    form = SQLFORM( db.node, node, fields=['picFile'], labels={'picFile':""},
                    comments=False, formstyle="divs" , showid = False,
                    _action = URL('ajaxedit','editphoto', args=[node.url]) )
                    
    if form.accepts(request.vars):
        response.view = "generic.load"
        node = db(db.node.url == request.args(0)).select().first()
        db.syslog.insert(action="Edited Page", target=node.id, target2="photo")
        return dict(t=IMG(_src=URL('default','thumb',args=[300,300,node.picFile])))
            
    else:
        response.view = "htmlblocks/edit_pict_form.html"
        return dict(node=node, form=form)

@auth.requires_login()
def link():
    # Find the node we are trying to update
    node = get_node_or_404( request.args(0) )
    node2 = get_node_or_404( request.args(1) )
    
    # Check node permissions
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node")
        
    if is_linked(node, node2):
        raise HTTP(405, "Already Linked")
        
    if node.id == node2.id:
        raise HTTP(405, "Can't Link to Self")
        
    db.linkTable.insert(nodeId=node, linkId=node2)
    db.syslog.insert(action="Linked Page", target=node.id, target2=node2.id)
    raise HTTP(200, "Ok, link made")


@auth.requires_login()
def unlink():
    # Find the node we are trying to update
    node = get_node_or_404( request.args(0) )
    node2 = get_node_or_404( request.args(1) )
    
    # Check node permissions
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node")
        
    db((db.linkTable.nodeId == node) & (db.linkTable.linkId == node2)).delete()
    db((db.linkTable.nodeId == node2) & (db.linkTable.linkId==node)).delete() 
    db.syslog.insert(action="Unlinked Page", target=node.id, target2=node2.id)
        
    raise HTTP(200, "Ok, link removed")

@auth.requires_login()
def watch():
    node = get_node_or_404( request.args(0) )
    the_cid = request.vars.cid or 'watch_link'
    
    if add_rem_watch(node, True):
        response.view = "generic.load"
        return A(SPAN(SPAN(_class="check icon"),'Unwatch'),_class="middle negative pill button", _href=URL('ajaxedit','unwatch',args=node.url), cid=the_cid, _title="Remove this page from your watch list.")
        
    else:
        raise HTTP(405, 'Already watched')
    
@auth.requires_login()
def unwatch():
    node = get_node_or_404( request.args(0) )
    the_cid = request.vars.cid or 'watch_link'
    
    if add_rem_watch(node, False):
        response.view = "generic.load"
        return A(SPAN(SPAN(_class="check icon"),'Watch'),_class="middle pill button", _href=URL('ajaxedit','watch',args=node.url), cid=the_cid, _title="Add this page to your watch list.")
    else:
        raise HTTP(405, 'Not watched')

@auth.requires_login()
def watchemail():
    if request.args(0) == "True":
        auth.user.email_watch = True
        db(db.auth_user.id == auth.user.id).update(email_watch=True)
        session.auth.user.email_watch = True
        response.view = "generic.load"
        return "Daily Email Enabled, " + A('Disable Daily Email', _href=URL('ajaxedit','watchemail',args='False'), _class="pill negative button", cid='watch_email').xml()
    else:
        auth.user.email_watch = False
        db(db.auth_user.id == auth.user.id).update(email_watch=False)
        session.auth.user.email_watch = False
        response.view = "generic.load"
        return "Daily Email Disabled, " + A('Enable Daily Email', _href=URL('ajaxedit','watchemail',args='True'), _class="pill button", cid='watch_email').xml()

@auth.requires_login()
def tag_toggle():
    if not request.vars.tag:
        raise HTTP(404, "Tag Required")
        
    new_tag = request.vars.tag.replace("_", " ")

    node = get_node_or_404( request.args(0) )
    
    if not can_edit(node):
        raise HTTP(403, "Not allowed to edit this node")
        
    if node.tags == None:
        node.tags = []
    if new_tag in node.tags:
        old_tags = node.tags[:]
        node.tags.remove(new_tag)
        node.update_record(tags=node.tags)
        db.syslog.insert(action="Edited Page", target=node.id, target2="tags")

        page_ref_support(node.tags, old_tags, node.id)

        raise HTTP(200, 'Tag Removed')
    else:
        node.update_record(tags=node.tags+[new_tag])
        db.syslog.insert(action="Edited Page", target=node.id, target2="tags")

        page_ref_support(node.tags+[new_tag], node.tags, node.id)

        raise HTTP(200, 'Tag Added')
        
@auth.requires_login()
def blog_tag_toggle():
    if not request.vars.tag:
        raise HTTP(404, "Tag Required")
        
    new_tag = request.vars.tag.replace("_", " ")

    #node = get_node_or_404( request.args(0) )
    blog = db(db.blog.id==request.args(0)).select().first()
    
    
    if not can_edit(blog.nodeId):
        raise HTTP(403, "Not allowed to edit this node")
        
    
    if not blog:
        raise HTTP(404, 'Blog entry not found')
        
    if blog.tags == None:
        blog.tags = []
    if new_tag in blog.tags:
        old_tags = blog.tags[:]
        blog.tags.remove(new_tag)
        blog.update_record(tags=blog.tags)
        db.syslog.insert(action="Edited Blog Entry", target=blog.nodeId.id, target2=blog)

        blog_ref_support(blog.tags, old_tags, blog.id)

        raise HTTP(200, 'Tag Removed')
    else:
        blog.update_record(tags=blog.tags+[new_tag])
        db.syslog.insert(action="Edited Blog Entry", target=blog.nodeId.id, target2=blog)

        blog_ref_support(blog.tags+[new_tag], blog.tags, blog.id)

        raise HTTP(200, 'Tag Added')

        
@auth.requires_login()
def feed_tag_toggle():
    if not request.vars.tag:
        raise HTTP(404, "Tag Required")
        
    new_tag = request.vars.tag.replace("_", " ")
    feed = db(db.rss_entry.id==request.args(0)).select().first()
    
    if not feed:
        raise HTTP(404, 'feed entry not found')
    
    node_owner = db(db.node.feeds.contains(feed.feed.id)).select().first()
    if not can_edit(node_owner):
        raise HTTP(403, "Not allowed to edit this node")
        
    if feed.tags == None:
        feed.tags = []
        
    if new_tag in feed.tags:
        old_tags = feed.tags[:]
        feed.tags.remove(new_tag)
        feed.update_record(tags=feed.tags)
        db.syslog.insert(action="Edited Feed Entry", target=node_owner.id, target2=feed.id)

        page_ref_support(feed.tags, old_tags, feed.id)

        raise HTTP(200, 'Tag Removed')
    else:
        feed.update_record(tags=feed.tags+[new_tag])
        db.syslog.insert(action="Edited Feed Entry", target=node_owner.id, target2=feed.id)

        feed_ref_support(feed.tags+[new_tag], feed.tags, feed.id)

        raise HTTP(200, 'Tag Added')
        

@auth.requires_membership("Site Admin")
def home_toggle():
    home_cat = db(db.highlights.title == request.args(0).replace("_", " ")).select().first()
    node = get_node_or_404(request.args(1))
    
    if not home_cat:
        raise HTTP(404, "Category not found")
    
    if node.id in home_cat.nodes:
        home_cat.nodes.remove(node.id)
        home_cat.update_record(nodes=home_cat.nodes)
        #db.syslog.insert(action="Edited Page", target=node.id, target2="tags")
        raise HTTP(200, 'Removed from %s' % home_cat.title)
    else:
        home_cat.update_record(nodes=home_cat.nodes+[node.id])
        #db.syslog.insert(action="Edited Page", target=node.id, target2="tags")
        raise HTTP(200, 'Added to %s' % home_cat.title)

@auth.requires_login()
def dropbox_upload():
    if get_quota_usage() > MAX_FILE_STORE:
        raise HTTP(400, "User has maxed quota")
        
    if request.vars.has_key("file_upload"):
        id = db.filebox.insert(Name=request.vars.file_upload.filename, File=db.filebox.File.store(request.vars.file_upload.file, request.vars.file_upload.filename))
        
        entry = db(db.filebox.id == id).select().first()
        
        #Force cache to be rebuilt
        quota = get_quota_usage(True)
        quota_text = get_quota_string()
        
        
        return URL("default","download", args=entry.File)
        
    raise HTTP(400, "No file upload found")
