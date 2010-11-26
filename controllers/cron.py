# coding: utf8
# try something like
def index(): return dict(message="hello from cron.py")

def send_watch_email():
    if request.env.remote_addr not in ["127.0.0.1","129.21.47.143"]:
        raise HTTP(401, 'unauthorized')
        
    #TODO Remove this
    _username_to_email()
    from datetime import datetime, timedelta
    for user in db(db.auth_user.id > 0).select(db.auth_user.email, db.auth_user.watch_nodes):
        if user.watch_nodes and len(user.watch_nodes):
            activity = db( 
                        # Target is always a page
                        ((db.syslog.target.belongs(user.watch_nodes)) | 
                        ( # Grab Target2 if Link and unlink pages
                          (
                            (db.syslog.action == 'Linked Page') |
                            (db.syslog.action == 'Unlinked Page')
                          ) & (db.syslog.target2.belongs(user.watch_nodes))
                        )) &
                        (db.syslog.date > datetime.now()-timedelta(days=1))
    
                     ).select(db.syslog.string_cache, db.syslog.date, limitby=(0,100), orderby=~db.syslog.id)
            email_message="""You have requested to be notified of updates on beta.innovation.rit.edu.<br><br>Resent Changes:<br>"""
            for change in activity:
                email_message += XML(change.string_cache, True, ['a']).flatten() + "<br />"
            
            if len(activity):
                mail.send(user.email, "Beta.innovation.rit.edu Watched Page Updates", "<html>%s</html>" % email_message)
    
def _username_to_email():
    for user in db(db.auth_user.email == "").select():
        user.update_record(email = "%s@rit.edu" % user.username)
