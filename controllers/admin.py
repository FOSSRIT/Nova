# coding: utf8
# try something like
def index(): return dict(message="hello from admin.py")

@auth.requires_membership("Site Admin")
def email_dump():
    return dict(emails=db(db.auth_user.email!="").select(db.auth_user.email).as_list())
