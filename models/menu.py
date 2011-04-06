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
       ('Calendar', False, "http://www.rit.edu/academicaffairs/centerforstudentinnovation/?page_id=69", []),
       ('Fellows', False, URL(request.application,'main','node',args='Fellows'), []),
    ]),
    ('Browse', False, "#", [
        ('Tags', False, URL(request.application,'main','tags'), []),
        ('Needs', False, URL(request.application, 'browse', 'index', vars={'attribute':'Needs'}), []),
        ('Skills', False, URL(request.application, 'browse', 'index', vars={'attribute':'Skills'}), []),
    ]),
]
    
#Dynamically add types to main menu
menu_types = db(db.nodeType.value!=None).select()
for mnu_item in menu_types:
    response.menu.append((mnu_item.value, False, URL(request.application, 'main', 'category/%s' % mnu_item.value ),[]))


# RSS HANDELING
rss_items = []
def addRss(name, url, title):
    rss_items.append( (name, url, title) )

def printRssHeader():
    if rss_items:
        return XML("\n".join(["<link rel=\"alternate\" type=\"application/atom+xml\" title=\"%s\" href=\"%s\" />" % (name, url) for name, url, title in rss_items]))
    else:
        return ""

def printRss():
    if rss_items:
        return DIV(
            IMG(_src=URL('static','images/Feed_32x32.png'), _width="10px", _height="10px", _style="vertical-align: middle;"),
            UL([LI(A(name, _href=url, _title=title), _style="display: inline; padding-left: 5px;") for name, url, title in rss_items], _style="padding: 0px; display:inline;"))
            
    else:
        return ""
