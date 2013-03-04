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
        if isinstance( tags, list):
            ret = UL(_class='comma-separated')
            [ret.append(A(tag, _href=URL('browse','tags', args=tag, extension=""))) for tag in tags]
        else:
            ret = tags
        return ret
    else:
        return "No Tags Found"
        
def tags_2_text(tags):
    if tags:
        return ", ".join(tags)
    else:
        return "No Tags Found"

def convert_bytes(bytes):
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2fT' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2fG' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2fM' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.2fK' % kilobytes
    else:
        size = '%.2fb' % bytes
    return size

def get_quota_usage(rebuild_cache=False):
    if session.sum and not rebuild_cache:
        return session.sum
        
    sum = db(db.filebox.owner == auth.user_id).select('sum(filebox.size)').first()
    sum = sum._extra['sum(filebox.size)']
    
    session.sum = sum
    return sum
    
def get_quota_string():
    sum = float( get_quota_usage() or 0)
    return "%.2f%% of available space (%s/%s)" % ((sum/MAX_FILE_STORE*100), convert_bytes(sum), convert_bytes(MAX_FILE_STORE))


def _ref_support(new_tags, old_tags, item_id, item_tag):
    # Test for new tags
    for tag in set(new_tags or []) - set(old_tags or []):
        if tag == "":
            continue

        test_node = db(db.node.url==tag).select().first()
        if test_node:
            db.syslog.insert(target=test_node.id, action="Refereced by %s" % item_tag, target2=item_id)

    # Test for removed tags
    for tag in set(old_tags or []) - set(new_tags or []):
        if tag == "":
            continue

        test_node = db(db.node.url==tag).select().first()
        if test_node:
            db.syslog.insert(target=test_node.id, action="Derefereced by %s" % item_tag, target2=item_id)


def blog_ref_support(new_tags, old_tags, blog_id ):
    _ref_support(new_tags, old_tags, blog_id, "Blog")

def page_ref_support(new_tags, old_tags, page_id ):
    _ref_support(new_tags, old_tags, page_id, "Page")

def feed_ref_support(new_tags, old_tags, page_id ):
    _ref_support(new_tags, old_tags, page_id, "Feed")

def node_pic(node, width=125, height=125, square=True):
    return URL('default','thumb',args=[width,height,node_pic_url(node)], vars={'square':square}, extension="")
        #URL('static', 'images', args='placeholder_thumb.png')

def node_pic_url(node):
    return node['picFile'] if node['picFile'] else node['type']['icon']
