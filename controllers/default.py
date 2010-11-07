# -*- coding: utf-8 -*- 

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################  

def index(): redirect('http://%s/%s/%s/' % (request.env.http_host, request.application, "main"))
def not_in_beta():
    return dict()
    
def user():
    """
    exposes:
    http://..../[app]/default/user/login 
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    
    # THIS IS A HACK: It fixes usernames coming in in mixed case.
    # The database is set to fix this, but the LDAP auth seems to cause
    # problems by bypassing checks.  So this forces the username to be
    # Lowercase before it gets processed by auth().
    if request.vars.username:
        request.vars.username = request.vars.username.lower()
        response.flash = request
    if request.post_vars.username:
        request.post_vars.username = request.post_vars.username.lower()

    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    del response.headers['Cache-Control']
    del response.headers['Pragma']
    del response.headers['Expires']
    response.headers['Cache-Control'] = "max-age=3600"
    return response.download(request,db)

def thumbnail():
    import os.path
    import Image
    
    del response.headers['Cache-Control']
    del response.headers['Pragma']
    del response.headers['Expires']
    response.headers['Cache-Control'] = "max-age=3600"
    
    #request Path
    request_sorce_path = os.path.join(request.folder, 'uploads', request.args(0))
    request_path = os.path.join(request.folder, 'uploads','thumb', request.args(0))
    #return dict(sorce=request_sorce_path, thumb=request_path)
    if os.path.exists(request_path):
        return response.stream(open(request_path, 'rb'))
    
    elif os.path.exists(request_sorce_path):
        thumb = Image.open(request_sorce_path)
        thumb.thumbnail((150,150), Image.ANTIALIAS)
        try:
            thumb.save(request_path)
        except KeyError:
            thumb.save(request_path, "JPEG")
        
        return response.stream(open(request_path, 'rb'))
    else:
        raise HTTP(404, "Image not found")

def mini_thumb():
    import os.path
    import Image
    
    del response.headers['Cache-Control']
    del response.headers['Pragma']
    del response.headers['Expires']
    response.headers['Cache-Control'] = "max-age=3600"
    
    #request Path
    request_sorce_path = os.path.join(request.folder, 'uploads', request.args(0))
    request_path = os.path.join(request.folder, 'uploads','mini_thumb', request.args(0))
    #return dict(sorce=request_sorce_path, thumb=request_path)
    if os.path.exists(request_path):
        return response.stream(open(request_path, 'rb'))
    
    elif os.path.exists(request_sorce_path):
        thumb = Image.open(request_sorce_path)
        thumb.thumbnail((40,40), Image.ANTIALIAS)
        try:
            thumb.save(request_path)
        except KeyError:
            thumb.save(request_path, "JPEG")
        
        return response.stream(open(request_path, 'rb'))
    else:
        raise HTTP(404, "Image not found")
def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()
