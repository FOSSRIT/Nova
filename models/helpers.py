# coding: utf8

def add_rem_watch(node, add):
    if add:
        if not auth.user.watch_nodes:
            db(db.auth_user.id == auth.user.id).update(watch_nodes=[node.id])
            session.auth.user.watch_nodes = [node.id]
            return True
            
        elif node.id not in auth.user.watch_nodes:
            db(db.auth_user.id == auth.user.id).update(watch_nodes=auth.user.watch_nodes + [node.id])
            session.auth.user.watch_nodes = auth.user.watch_nodes + [node.id]
            return True
    
        else:
            return False
    else:
        if node.id in auth.user.watch_nodes:
            auth.user.watch_nodes.remove(node.id)
            db(db.auth_user.id == auth.user.id).update(watch_nodes=auth.user.watch_nodes)
            session.auth.user.watch_nodes = auth.user.watch_nodes
            return True
        else:
            return False

def tags_2_html(tags):
    if tags:
        ret = UL(_class='comma-separated')
        [ret.append(A(tag, _href=URL('main','tags', args=tag))) for tag in tags]
        return ret
    else:
        return "No Tags Found"
