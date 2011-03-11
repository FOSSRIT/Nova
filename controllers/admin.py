# coding: utf8
# try something like
def index(): return dict(message="hello from admin.py")

@auth.requires_membership("Site Admin")
def email_dump():
    return dict(emails=db(db.auth_user.email!="").select(db.auth_user.email).as_list())

@auth.requires_membership("Site Admin")
def image_resize():
    import Image
    import os
    
    request_sorce_path = os.path.join(request.folder, 'uploads')
    
    badFiles = []
    goodFiles = []
    for file_path in os.listdir(request_sorce_path):
        if file_path == "thumb":
            continue
        
        file_full_path = os.path.join(request_sorce_path,file_path)
        
        try:
            thumb = Image.open(file_full_path)
        except:
            badFiles += [file_path]
            
        thumb.thumbnail((800,800), Image.ANTIALIAS)
        try:
            thumb.save(file_full_path)
            goodFiles += [file_path]
        except KeyError:
            if thumb.mode != "RGB":
               thumb = thumb.convert("RGB")
            thumb.save(file_full_path, "JPEG")
            
    return dict(files_failed=badFiles, goodFiles=goodFiles)

@auth.requires_membership("Site Admin")
def cleanup_dead_ref():
    dead_nodes = []
    #Remove dead watched pages
    for user in db((db.auth_user.id > 0)).select():
        if user.watch_nodes and len(user.watch_nodes):
            ref_remove = []
            for node in user.watch_nodes:
                if not db(db.node.id == node).count():
                    dead_nodes += [node]
                    ref_remove += [node]
                    
            if len( ref_remove ):
                nodelst = user.watch_nodes
                for i in ref_remove:
                    nodelst.remove(i)
                user.update_record(watch_nodes=nodelst)
                
    dict(dead_nodes=dead_nodes)
   
@auth.requires_membership("Site Admin") 
def feeds_to_db():
    errors = []
    
    for node in db(db.node.feeds != None).select():
        feed_id = []
        for feed_string in node.feeds:
            if (feed_string, None) == db.rss_feed.link.validate(feed_string):
                id = db.rss_feed.insert(link=feed_string)
                feed_id.append(id)
            else:
                errors.append("%s: %s"% ( node.name, feed_string))
        node.update_record(feeds=feed_id, modified=node.modified)
    return dict(errors=errors)
