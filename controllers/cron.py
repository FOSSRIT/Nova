# coding: utf8
# try something like
def index(): return dict(message="hello from cron.py")

def send_watch_email():
    if request.env.remote_addr not in ["127.0.0.1","129.21.142.164"]:
        raise HTTP(401, 'unauthorized')
        
    #TODO Remove this
    _username_to_email()
    from datetime import datetime, timedelta
    for user in db((db.auth_user.id > 0) & (db.auth_user.email_watch == True)).select(db.auth_user.email, db.auth_user.watch_nodes):
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
            email_message=""
            for change in activity:
                email_message += XML(change.string_cache, True, ['a']).flatten() + "<br />"
            
            if len(activity):
                mail.send(user.email, "NOVA Watched Page Updates", 
                """<html>
                <head>
                    <base href='http://nova.innovation.rit.edu'>
                </head>
                <body>
                    You have requested to be notified of updates on nova.innovation.rit.edu.<br><br>
                    
                    Recent Changes:<br>
                    %s<br><br>
                    
                    ---<br>
                    This is an automated email. Do Not Reply, this inbox is not monitored.<br>
                    If you wish to disable this email please visit your <a href='/csi2/main/watched'>Watched Pages</a> and disable this notification.
                </body>
                </html>""" % email_message)
    
def _username_to_email():
    for user in db(db.auth_user.email == "").select():
        user.update_record(email = "%s@rit.edu" % user.username)
        
def hourly():
    if request.env.remote_addr not in ["127.0.0.1","129.21.47.143"]:
        raise HTTP(401, 'unauthorized')
        
    return "<br>".join(update_feeds())
