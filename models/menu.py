# -*- coding: utf-8 -*- 

response.title = "Center for Student Innovation"

##########################################
## this is the main application menu
## add/remove items as required
##########################################

response.menu = [
    [T('Index'),  URL(request.application,'default','index')],
    ]
    
#Dynamically add types to main menu
menu_types = db(db.nodeType.value!=None).select()
for mnu_item in menu_types:
    response.menu.append([mnu_item.value, URL(request.application, 'main', 'view/%s' % mnu_item.value )])
