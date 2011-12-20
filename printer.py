import Image, ImageDraw
#For Py2exe towork
import JpegImagePlugin, GifImagePlugin, PngImagePlugin
Image._initialized = 2

from reportlab.pdfgen import canvas

import os,os.path
from math import ceil

#Size are in pixel

BLACK=0  

from actions import template_empty
from propgrid import UnSerialize

from reportlab.lib.units import cm
#from config import print_size
import reportlab.lib.pagesizes
#psize=getattr(reportlab.lib.pagesizes,print_size)
psize=reportlab.lib.pagesizes.A4
from config import p2cm
A4=psize

from reportlab.lib.colors import black
from reportlab.lib.utils import ImageReader
from cStringIO import StringIO
from config import   DEBUG


def cb(pnum):
    from __main__ import frame
    frame.statusBar1.SetStatusText('Page %d done'%pnum)

def format(decklisting,dst,deckname='page',fitting_size=None,templates=None):
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
    
    from config import PRINT_ENGINE
    
    ENGINES[PRINT_ENGINE](deckname, dst, fitting_size, imgs, imgs_back, templates)
    if DEBUG:
        print "Done"
           
def pdfcreate_image(deckname, dst, fitting_size, front,back, templates):
    output=canvas.Canvas(os.path.join(dst,deckname+".pdf"),psize,cropMarks=False)
    output.setTitle(deckname)
    output.setStrokeColor(black)
    output.setFont('Times-Roman',10)
    output.setPageCallBack(cb)
    import config
    if fitting_size is None:
        fitting_size=(config.px,config.py)
    else:
        fitting_size=[p2cm(i) for i in fitting_size]
    a4_size_x,a4_size_y=(config.a4x,config.a4y)
    x,y=fitting_size
    left=p2cm(config.left)
    right=p2cm(config.right)
    top=p2cm(config.top)
    bottom=p2cm(config.bottom)
    sheet_left=p2cm(config.sheet_left)
    sheet_top=p2cm(config.sheet_top)
    x_gap=left+right+x+p2cm(5)
    y_gap=top+bottom+y+p2cm(5)
    NUM_ROW=int((a4_size_x-top)/x_gap)
    NUM_COL=int((a4_size_y-left)/y_gap)
    PICT_BY_SHEET=NUM_COL*NUM_ROW
    deckname=deckname.lower().split('.')[0]
    if DEBUG:
        print 'Preparing %d picts by sheet (%d by %d)'%(PICT_BY_SHEET, NUM_ROW, NUM_COL),
        _t=""
        if dual: _t=" BACK mode"
        print _t
    maxlen=max(len(front),len(back))
    for i in range(int(ceil((float(maxlen)/PICT_BY_SHEET)))):
        for dual,imgs in zip((False,True),(front,back)):
            if not imgs:
                continue
            sheet_imgs=imgs[PICT_BY_SHEET*i:PICT_BY_SHEET*(i+1)]
            if not sheet_imgs:
                continue
            sheet_imgs.reverse()
            #Write the fiiting size info for deck + date
            from datetime import date
            text="Printed on the %s. fitting size: %s"%(date.today().strftime('%d/%m/%y'),fitting_size)
            output.drawString(sheet_left,a4_size_y-sheet_left,text)        
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
                        card=T.draw(os.path.join(config.card_folder,s.encode('cp1252')),fitting_size,values)
                    except IndexError:#done ! 
                        break
                    if rotated:
                        card=card.rotate(90)
    
                    #No more resizing: this is being handled by draw image bounding box                
                    card=card.resize([config.cm2p(_i) for _i in fitting_size])
    
                    #Start point is reverted from right border if dual
                    if not dual:
                        startx=row*x_gap + sheet_left
                    else:
                        startx=a4_size_x - ((row+1)*x_gap + sheet_left)
                    starty=col*y_gap + sheet_top
                    #Line vertical:
                    output.line(startx*cm,0,startx*cm,a4_size_y*cm)
                    output.line(cm*(startx+left+right+x),0,cm*(startx+left+right+x),a4_size_y*cm)
                    #Line horizontal
                    output.line(0,starty*cm,a4_size_x*cm,starty*cm)
                    output.line(0,(starty+top+bottom+y)*cm,a4_size_x*cm,(starty+top+bottom+y)*cm)
                    #~ #black rectangle
                    if config.BLACK_FILLING:
                        output.rect(startx*cm,starty*cm, (left+right+x)*cm, (top+bottom+y)*cm,fill=True)
                    #PAste image
                    c=StringIO()
                    card.save(c, format="PNG")
                    c.seek(0) #Rewind it
                    ir = ImageReader(c)
                    #print 'Pasting Image at cm:',startx+left,starty+top, x,y,fitting_size
                    output.drawImage(ir,(startx+left)*cm,(starty+top)*cm,x*cm,y*cm)
            output.showPage()
            #In dual mode, save as back
    output.save()

def wxcreate_image(deckname, dst, fitting_size, front,back, templates):
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
    for imgs,dual in zip((front,back),(False,True)):
        if DEBUG:
            print 'Preparing %d picts by sheet (%d by %d)'%(PICT_BY_SHEET, NUM_ROW, NUM_COL),
            _t=""
            if dual: _t=" BACK mode"
            print _t
        x,y=fitting_size
        for i in range(int(ceil((float(len(imgs))/PICT_BY_SHEET)))):
            sheet=wx.EmptyBitmapRGBA(a4_size_x,a4_size_y,255,255,255,255)
            draw=wx.MemoryDC(sheet)
            sheet_imgs=imgs[PICT_BY_SHEET*i:PICT_BY_SHEET*(i+1)]
            sheet_imgs.reverse()
            #Write the fiiting size info for deck + date
            from datetime import date
            text="Printed on the %s. fitting size: %s"%(date.today().strftime('%d/%m/%y'),fitting_size)
            draw.DrawText(text,sheet_left, sheet_top/2)
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
                        _target=s.encode('cp1252')
                        if not os.path.isfile(_target):
                            _target=os.path.join(card_folder,s.encode('cp1252'))
                        card=T.format(wx.Image(_target).Rescale(*fitting_size),values)
                    except IndexError:#done ! 
                        break
                    if rotated:
                        card=card.Rotate90()
                    #Rotate card if card.width > card height & x>y
                    _w,_h=card.GetSize().Get()
                    #if x>y & _w>_h:
                    #    card=card.rotate(90)
                    res=card.Rescale(*fitting_size)
                    #Start point is reverted from right border if dual
                    if not dual:
                        startx=row*x_gap + sheet_left
                    else:
                        startx=a4_size_x - ((row+1)*x_gap + sheet_left)
                    starty=col*y_gap + sheet_top
                    #Line vertical:
                    draw.DrawLine(startx,0,startx,a4_size_y)
                    draw.DrawLine(startx+left+right+x,0,startx+left+right+x,a4_size_y)
                    #Line horizontal
                    draw.DrawLine(0,starty,a4_size_x,starty)
                    draw.DrawLine(0,starty+top+bottom+y,a4_size_x,starty+top+bottom+y)
                    #~ #black rectangle
                    if BLACK_FILLING:
                        draw.DrawRectangle(startx,starty, left+right+x, top+bottom+y)
                    draw.DrawBitmap(res.ConvertToBitmap(),startx+left,starty+top,True)
            del draw
            #Retrieve print format in wx
            if PRINT_FORMAT.upper()=='JPG':
                PRINT_FORMAT='JPEG'
            p=getattr(wx,'BITMAP_TYPE_%s'%PRINT_FORMAT.upper())
            #In dual mode, save as back
            if dual:
                
                sheet.SaveFile(os.path.join(dst,'%s_%02d_back.%s'%(deckname,i+1,PRINT_FORMAT)),p)
            else:
                sheet.SaveFile(os.path.join(dst,'%s_%02d.%s'%(deckname,i+1,PRINT_FORMAT)),p)

        
def pilcreate_image(deckname, dst, fitting_size, front, back, templates):
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
    for imgs,dual in zip((front,back),(False,True)):
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
    

ENGINES=dict("wx":wxcreate_image,'pil':pilcreate_image,'pdf':pdfcreate_image)