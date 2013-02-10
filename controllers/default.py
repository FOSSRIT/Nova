# -*- coding: utf-8 -*- 

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################  

def index():
    redirect('http://%s/%s/%s/' % (request.env.http_host, request.application, "main"))
    
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
    if request.post_vars.username:
        request.post_vars.username = request.post_vars.username.lower()
    
    if request.post_vars.password == "":
        session.flash="You attempted to login without a password"
        redirect(URL('default','user',args="login"))

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

def thumb():
    if not request.args(2):
        raise HTTP(404, "Image Not Found")
    del response.headers['Cache-Control']
    del response.headers['Pragma']
    del response.headers['Expires']
    response.headers['Cache-Control'] = "max-age=3600"

    import os.path
    import gluon.contenttype as c
    try:
        size_x = int(request.args(0))
        size_y = int(request.args(1))
    except:
        raise HTTP(400, "Invalid Image Dementions")
        
    if request.vars.square:
        pathStr = "%d_%d_%s_square"
    else:
        pathStr = "%d_%d_%s"
        
    request_path = os.path.join(request.folder, 'uploads','thumb', pathStr % (size_x, size_y, request.args(2)))
    request_sorce_path = os.path.join(request.folder, 'uploads', request.args(2))
    
    if os.path.exists(request_path):
        response.headers['Content-Type'] = c.contenttype(request_path) 
        return response.stream(open(request_path, 'rb'))
    
    elif os.path.exists(request_sorce_path):
        import Image
        
        THUMB_SIZE = size_x, size_y
        
        thumb = Image.open(request_sorce_path)
        if request.vars.square:
            width, height = thumb.size
    
            if width > height:
               delta = width - height
               left = int(delta/2)
               upper = 0
               right = height + left
               lower = height
            else:
                delta = height - width
                left = 0
                upper = int(delta/2)
                right = width
                lower = width + upper
    
            thumb = thumb.crop((left, upper, right, lower))
        thumb.thumbnail(THUMB_SIZE, Image.ANTIALIAS)
        try:
            thumb.save(request_path)
        except KeyError:
            thumb.save(request_path, "JPEG")

        response.headers['Content-Type'] = c.contenttype(request_path) 
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

@auth.requires_login()
def optinout():
    form = SQLFORM( db.auth_user, db.auth_user(auth.user_id),
            showid = False, fields=['optout'], submit_button="Save")
            
    if form.accepts(request.vars, session):
        response.flash = "Your changes have been saved" 
    return dict(form=form)
