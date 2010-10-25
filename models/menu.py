# -*- coding: utf-8 -*- 

response.title = "Center for Student Innovation"

##########################################
## this is the main application menu
## add/remove items as required
##########################################
response.menu = [
    ('Home', False, URL(request.application,'main','index'), []),
    ('About', False, URL(request.application,'main','about'), [
       ('Blog', False, "http://innovation.rit.edu", []),
       ('Courses', False, "http://www.rit.edu/academicaffairs/centerforstudentinnovation/collaborative-innovation-courses-for-winter-make-cool-stuff/", []),
       ('Events', False, "http://www.rit.edu/academicaffairs/centerforstudentinnovation/?page_id=69", []),
       ('Engage', False, "http://www.rit.edu/academicaffairs/centerforstudentinnovation/?page_id=230", []),
          ('Fellows', False, "http://beta.innovation.rit.edu/csi2/main/node/Fellows", []),
    ])
]
    
#Dynamically add types to main menu
menu_types = db(db.nodeType.value!=None).select()
for mnu_item in menu_types:
    response.menu.append((mnu_item.value, False, URL(request.application, 'main', 'category/%s' % mnu_item.value ),[]))
