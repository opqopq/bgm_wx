import Image, ImageDraw
#For Py2exe towork
import JpegImagePlugin, GifImagePlugin, PngImagePlugin
Image._initialized = 2

import os
from math import ceil

#Size are in pixel

BLACK=0  

from actions import template_empty
from propgrid import UnSerialize

def format(decklisting,dst,deckname='page',fitting_size=None,templates=None):
    from config import   DEBUG
    if DEBUG:
        print 'Formating deck ',deckname
    ##Base hypothesis: 
    ##   all elements are the same SIZE, coerced to fitting_size
    ##   size in pixel
    imgs=[]
    imgs_back=[]
    #Decklisting is a dict
    #Mapping a patch (key) to => oqt,_, dual boolean,rotated boolean
    for card in decklisting:
        #Name,Qt,Path,Fit,Dual,Rotated,Template=None,Values=None
        if not card.Dual:
            imgs.extend([(card.Path,card.Rotated,card.Template,card.Values)]*card.Qt)
        else:
            imgs_back.extend([(card.Path,card.Rotated,card.Template,card.Values)]*card.Qt)
    if len(imgs)!=len(imgs_back) and len(imgs_back):
        print 'WARNING: No the same number of image & back (%d fronts vs %d backs)'%(len(imgs),len(imgs_back))
    if imgs:
        create_image(deckname, dst, fitting_size, imgs, templates,dual=False)
    if imgs_back:
        create_image(deckname, dst, fitting_size, imgs_back, templates,dual=True)
    if DEBUG:
        print "Done"
           
def create_image(deckname, dst, fitting_size, imgs, templates,dual):
    from config import left, right, bottom, top, a4_size, DEBUG, PRINT_FORMAT, card_folder, sheet_left, sheet_top, BLACK_FILLING
    if fitting_size is None:
        fitting_size=print_size
    a4_size_x,a4_size_y=a4_size
    x,y=fitting_size
    x_gap=left+right+x+5
    y_gap=top+bottom+y+5
    NUM_ROW=(a4_size[0]-top)/x_gap
    NUM_COL=(a4_size[1]-left)/y_gap
    PICT_BY_SHEET=NUM_COL*NUM_ROW
    deckname=deckname.lower().split('.')[0]
    if DEBUG:
        print 'Preparing %d picts by sheet (%d by %d)'%(PICT_BY_SHEET, NUM_ROW, NUM_COL),
        _t=""
        if dual: _t=" BACK mode"
        print _t
    x,y=fitting_size
    for i in range(int(ceil((float(len(imgs))/PICT_BY_SHEET)))):
        sheet=Image.new('RGBA', a4_size,(255,255,255,255))
        draw=ImageDraw.Draw(sheet)
        sheet_imgs=imgs[PICT_BY_SHEET*i:PICT_BY_SHEET*(i+1)]
        sheet_imgs.reverse()
        #Write the fiiting size info for deck + date
        from datetime import date
        text="Printed on the %s. fitting size: %s"%(date.today().strftime('%d/%m/%y'),fitting_size)
        draw.text((sheet_left,sheet_top/2),text)
        for col in range(NUM_COL):
            for row in range(NUM_ROW):
                try:
                    s,rotated,templateName,values=sheet_imgs.pop()
                    #print s,rotated,templateName,values
                    T=templates.get(templateName,None)
                    if not T:
                        #print templateName,T, templates.keys()
                        T= template_empty
                    #else:
                    #print 'using template',T.name
                    card=T.draw(os.path.join(card_folder,s.encode('cp1252')),fitting_size,values)
                except IndexError:#done ! 
                    break
                if rotated:
                    card=card.rotate(90)
                #Rotate card if card.width > card height & x>y
                _w,_h=card.size
                #if x>y & _w>_h:
                #    card=card.rotate(90)
                res=card.resize(fitting_size)
                #Start point is reverted from right border if dual
                if not dual:
                    startx=row*x_gap + sheet_left
                else:
                    startx=a4_size_x - ((row+1)*x_gap + sheet_left)
                starty=col*y_gap + sheet_top
                #Line vertical:
                draw.line((startx,0)+(startx,a4_size_y),fill=BLACK)
                draw.line((startx+left+right+x,0)+(startx+left+right+x,a4_size_y),fill=BLACK)
                #Line horizontal
                draw.line((0,starty)+(a4_size_x,starty),fill=BLACK)
                draw.line((0,starty+top+bottom+y)+(a4_size_x,starty+top+bottom+y),fill=BLACK)
                #~ #black rectangle
                if BLACK_FILLING:
                    draw.rectangle((startx,starty, startx+left+right+x, starty+top+bottom+y), fill=BLACK)
                sheet.paste(res,(startx+left,starty+top))
        del draw
        #In dual mode, save as back
        if dual: sheet.save(os.path.join(dst,'%s_%02d_back.%s'%(deckname,i+1,PRINT_FORMAT)))
        else:   sheet.save(os.path.join(dst,'%s_%02d.%s'%(deckname,i+1,PRINT_FORMAT)))



