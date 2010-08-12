# -*- coding: utf-8 -*- 

response.title = "Center for Student Innovation"

##########################################
## this is the main application menu
## add/remove items as required
##########################################

response.menu = [
    [T('Home'),  URL(request.application,'main','index')],
    [T('About'),  URL(request.application,'main','about')]
    ]
    
#Dynamically add types to main menu
menu_types = db(db.nodeType.value!=None).select()
for mnu_item in menu_types:
    response.menu.append([mnu_item.value, URL(request.application, 'main', 'view/%s' % mnu_item.value )])
