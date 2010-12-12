# coding: utf8
# try something like
def index(): return dict(message="hello from admin.py")

@auth.requires_membership("Site Admin")
def email_dump():
    return dict(emails=db(db.auth_user.email!="").select(db.auth_user.email).as_list())

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
