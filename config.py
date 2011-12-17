import os
from os.path import join
from ConfigParser import SafeConfigParser, NoSectionError, NoOptionError
cp=SafeConfigParser()



import sys,os

SRC='bgm.ini'
##All size in pixel ?
#Table with section name, option name, variable name, default value, and function to be applyied to it
configItem=[
        #Card Folder basis for all development
        ('card','src','card_folder',None, None),
        ('user','deckdir','deckdir','.', None),
        #Gap between card
        ('size','x_pad','x_pad',5,int),
        ('size','y_pad','y_pad',5,int),
        ('size','DPI','DPI',300,int),
        ('size','print_x','px',6.3,float),
        ('size','print_y','py',8.8,float),
        ('size','a4_x','a4x',21,float),
        ('size','a4_y','a4y',29.7,float),
        #Sheet Border
        ('sheetborder','left','sheet_left',8,int),
        ('sheetborder','top','sheet_top',10,int),
        #Card Border
        ('cardborder','top','top',10,int),
        ('cardborder','bottom','bottom',12,int),
        ('cardborder','left','left',8,int),
        ('cardborder','right','right',8,int),
        #Print Format
        ('print','format','PRINT_FORMAT','png',None),
        #Mse
        #MSE data
        ('mse','path','MSE_PATH','',None),
        ('mse','version','MSE_VERSION','0.3.9',None),
        #Black Filling - Card Filling between cards on the print page
        ('cardborder','filling','BLACK_FILLING',True,lambda x:str(x).lower()!='none'),
        #Debug,
        ('debug','activate_print','DEBUG',False,lambda x:str(x).lower()!='false'),
        #BGG
        ('bgg','img_browse','bgg_img_browse_url',"http://www.boardgamegeek.com/geekimagemodule.php?action=imagemodule&objecttype=thing&objectid=%d&gallery=all&sort=recent&instanceid=10&showcount=15&rowsize=15&pageid=%d&ajax=1",None),
        ('bgg','file_browse','bgg_file_browse_url',"http://boardgamegeek.com/geekfile.php?objecttype=thing&objectid=%%d&sort=recent&instanceid=16&pageid=%%d&action=module&ajax=1",None),
        ('bgg','link_browse','bgg_link_browse_url',"http://boardgamegeek.com/geekitem.php?instanceid=25&objecttype=thing&objectid=%%d&subtype=boardgame&pageid=%%d&sort=recent&view=weblinks&modulename=weblinks&callback=&showcount=10&action=linkeditems&ajax=1",None),
        ('bgg','search','bgg_search_url','http://www.boardgamegeek.com/xmlapi/search?search=%s',None),
]

__all__=[x[2] for x in configItem]
    
def getRunDir():
     try:
         sys.frozen
     except AttributeError:
         path = sys.argv[0]
     else:
         path = sys.executable

     return os.path.dirname(os.path.abspath(path)) 


cp.readfp(file(SRC,'rb'))

#Generic Treatment
for S,O,Name,Default,Apply in configItem:
    try:
        value=cp.get(S,O)
    except (NoSectionError,NoOptionError):
        value=Default
    if Apply:
        value=Apply(value)
    globals()[Name]=value
    
#Specifal Treatment depending on value    
##Card Folder
if not os.path.isdir(card_folder):
    card_folder=None
##Size of a card in the sheet:
print_size_x=int(round(px/2.54*DPI))
print_size_y=int(round(py/2.54*DPI))
a4_size_x=int(round(a4x/2.54*DPI))
a4_size_y=int(round(a4y/2.54*DPI))
print_size=(print_size_x,print_size_y)
a4_size=(a4_size_x,a4_size_y)

def cm2p(cm):
    return int(round(cm/2.54*DPI))
    
def p2cm(px):
    return int(round(px*2.54/DPI))
    

def get(section,option):
    try:
        value=cp.get(section,option)
    except NoSectionError:
        return None
    except NoOptionError:
        return None
    return value
    
def set(section,option,value):
    cp.set(section,option,value.encode('cp1252'))
    cp.write(file(SRC,'wb'))
    t=file(SRC,'rb').read().replace('\n',os.linesep)
    file(SRC,'wb').write(t)