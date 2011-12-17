from actions import Template, Script
import wx
from collections import OrderedDict
import os

class HexaPageScript(Script):
    global OrderedDict
    name=" Hexa Page Maker"
    help="Create a page with all image pasted as hexa image"
    column=OrderedDict()
    column['Destination Directory']=('dir',None)
    column['x step']=('int',0)
    column['y step']=('int',0)
    
    def run(self,mainframe,values=None):
        BLACK=0
        from config import card_folder, a4_size, PRINT_FORMAT, top, bottom,left,right,sheet_left, sheet_top
        from os.path import join,isfile
        import os, Image
        from math import sqrt, radians,ceil
        from actions import template_empty
        from propgrid import UnSerialize
        x_step=values['x step']
        y_step=values['y step']
        dst=values['Destination Directory']
        if not dst:
            dlg = wx.DirDialog(mainframe, "Choose a destination Directory", style=wx.DD_DEFAULT_STYLE, defaultPath=mainframe.deckdir)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    dst = dlg.GetPath()
                else:
                    return
            finally:
                dlg.Destroy()
        #Determine tuckbox size
        W,L=a4_size
        decklisting=mainframe.GetCurrentDeck()
        imgs_front=[]
        imgs_back=[]
        #Decklisting is a dict
        #Mapping a patch (key) to => oqt,_, dual boolean,rotated boolean
        for line in decklisting:
            [displayName,qt,cardPath,dual,rotated,template,value]=line
            #[cardPath,qt,dual,rotated,template,value]=line
            if not dual:
                imgs_front.extend([(cardPath,rotated,template,value)]*qt)
            else:
                imgs_back.extend([(cardPath,rotated,template,value)]*qt)
        #Determine the number of images by page
        x,y=mainframe.fitting_size
        x_gap=left+right+x+5-x_step
        y_gap=top+bottom+y+5 - y_step
        NUM_ROW=(a4_size[0]-top)/x_gap
        NUM_COL=(a4_size[1]-left-y_step)/y_gap
        PICT_BY_SHEET=NUM_COL*NUM_ROW
        for imgs,dual in zip((imgs_front,imgs_back),(False,True)):
            for i in range(int(ceil((float(len(imgs))/PICT_BY_SHEET)))):
                sheet=Image.new('RGBA', a4_size,(255,255,255,255))
                sheet_imgs=imgs[PICT_BY_SHEET*i:PICT_BY_SHEET*(i+1)]
                sheet_imgs.reverse()
                for col in range(NUM_COL):
                    for row in range(NUM_ROW):
                        try:
                            s,rotated,templateName,values=sheet_imgs.pop()
                            #print s,rotated,templateName,values
                            T=mainframe.templates.get(templateName,None)
                            if not T:
                                #print templateName,T, templates.keys()
                                T= template_empty
                            #else:
                            #print 'using template',T.name
                            card=T.draw(os.path.join(card_folder,s.encode('cp1252')),mainframe.fitting_size,values)
                        except IndexError:#done ! 
                            break
                        if rotated:
                            card=card.rotate(90)
                        #Rotate card if card.width > card height & x>y
                        _w,_h=card.size
                        #if x>y & _w>_h:
                        #    card=card.rotate(90)
                        res=card.resize(mainframe.fitting_size)
                        #Start point is reverted from right border if dual
                        _step=col%2*x_step
                        if not dual:
                            startx=row*x_gap + sheet_left + _step
                        else:
                            startx=a4_size_x - ((row+1)*x_gap + sheet_left+_step)
                        starty=col*y_gap + sheet_top
                        if col:
                            starty-=y_step
                        #print dual,_step,(startx+left,starty+top)
                        #mask=res.copy()
                        #mask.convert('L')#paste(128)#('1')
                        #mask.save('toto.png')
                        #res.putalpha(mask)
                        sheet.paste(res,(startx+left,starty+top))
                #Save & display
                suffix=""
                if dual: 
                    suffix="_back"
                if imgs:
                    sheet.save(os.path.join(dst,'ouput%d%s.png'%(i,suffix)))
        import os
        os.startfile(dst)

        
script_tb=HexaPageScript()
