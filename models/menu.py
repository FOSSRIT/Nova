# -*- coding: utf-8 -*- 

response.title = "Center for Student Innovation"

##########################################
## this is the main application menu
## add/remove items as required
##########################################

response.menu = [
    ['Home',  URL(request.application,'main','index'), []],
    ['About',  URL(request.application,'main','about'), [
       ['Courses',  "http://innovation.rit.edu/http://www.rit.edu/academicaffairs/centerforstudentinnovation/collaborative-innovation-courses-for-winter-make-cool-stuff/", []],
       ['Test2',  "#", []],
    ]],
    ['Blog', "http://innovation.rit.edu", []],
    ]
    
#Dynamically add types to main menu
menu_types = db(db.nodeType.value!=None).select()
for mnu_item in menu_types:
    response.menu.append([mnu_item.value, URL(request.application, 'main', 'category/%s' % mnu_item.value ),[]])
