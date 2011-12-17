from actions import Template, Script
import wx
from collections import OrderedDict

class GameBoxScript(Script):
    global OrderedDict
    name=" Gamebox Maker"
    help="Create a game box for current deck given 4 images: front, back, side (left+right), side (top-bottom)"
    column=OrderedDict()
    column['Destination file']=('file',None)
    column['front']=('file',None)
    column['back']=('file',None)
    column['side (left/right)']=('file',None)
    column['side (top/bottom)']=('file',None)
    column['Depth(cm)']=('float',0.0)
    column['Length(cm) - optional']=('float',0.0)
    column['Width(cm) - optional']=('float',0.0)

    def run(self,frame,values=None):
        return
        
script_gb=GameBoxScript()

class TuckBoxScript(Script):
    global OrderedDict
    name=" Tuckbox Maker"
    help="Create a tuck box for current deck given 4 images: front, back, side (left+right), side (top-bottom)"
    column=OrderedDict()
    column['Destination file']=('file',None)
    column['front']=('file',None)
    column['back']=('file',None)
    column['side (left/right)']=('file',None)
    column['side (top/bottom)']=('file',None)
    column['Depth(cm)']=('float',0.0)
    column['Length(cm) - optional']=('float',0.0)
    column['Width(cm) - optional']=('float',0.0)

    def run(self,mainframe,values=None):
        BLACK=0
        from config import card_folder, a4_size, PRINT_FORMAT
        from os.path import join,isfile
        from math import sqrt, radians
        dst=values['Destination file']
        DEPTH=values['Depth(cm)']
        LENGTH=values['Length(cm) - optional']
        WIDTH=values['Width(cm) - optional']
        if not dst:
            dlg = wx.FileDialog(mainframe, "Choose a destination file", mainframe.deckdir, "", "*.*", wx.SAVE| wx.OVERWRITE_PROMPT)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    dst = dlg.GetPath()
                else:
                    return
            finally:
                dlg.Destroy()
        front=values['front']
        if not isfile(front):
            front=None
        back=values['back']
        if not isfile(back):
            back=None
        sidelr=values['side (left/right)']
        if not isfile(sidelr):
            sidelr=None
        sidetb=values['side (top/bottom)']
        if not isfile(sidetb):
            sidetb=None
        #Determine tuckbox size
        width,length=mainframe.fitting_size
        from config import left, right, bottom, top, a4_size, DEBUG, PRINT_FORMAT, card_folder, sheet_left, sheet_top, BLACK_FILLING
        width+=left+right+5  + 10 #10 added to make some place for the card around it in the tuckbox
        length+=top+bottom+5 
        length=float(length+10)
        width=float(width+10)
        deep=10+float((mainframe.deckgrid.GetDeckSize()))* 2.5
        import config
        if DEPTH:
            deep=config.cm2p(DEPTH)
        if LENGTH:
            length=config.cm2p(LENGTH)
        if WIDTH:
            width=config.cm2p(WIDTH)
        #Create Tuckboxes lines
        import Image, ImageDraw
        #w,l=a4_size
        w=int(3*deep+2*width+1)
        l=int(3*deep+length +1)
        if sorted((w,l))>sorted(a4_size):
            print "won't fit in a4 page"
        _W,_L=reversed(a4_size)
        sheet=Image.new('RGB', (_W,_L),(255,255,255))
        draw=ImageDraw.Draw(sheet)
        #Draw necessary lines
        def ysym(y):
            return int(3*deep + length - y)
        iso= lambda x:x
        step=deep/4
        colors=[BLACK]*6
        for stopx,color in zip([deep,deep+width, 2*deep+width,2*(deep+width),2.9*deep+2*width],colors):
            draw.rectangle((0,deep+2*step,stopx,deep+2*step+length),outline=color)
        for func in (iso,ysym):
            draw.line((deep/2,func(deep), deep,func(deep)),fill=colors[0])
            draw.line((deep+width,func(deep), 3*deep/2+width,func(deep)),fill=colors[1])
            draw.line((deep,func(2*step), deep,func(deep+2*step)),fill=colors[2])
            draw.line((deep,func(2*step), deep+width,func(2*step)),fill=colors[3])
            draw.line((deep+width/4,func(0), deep+3*width/4,func(0)),fill=colors[4])
            draw.line((deep+width,func(2*step), deep+width,func(deep+2*step)),fill=colors[5])
            draw.arc((0,int(deep+2*step),int(deep/2),int(deep)),180,270,fill=BLACK)
        #Now for the folding bottom rectangle, only at the bottom
        draw.rectangle((2*deep+width,length+step+deep,2*(deep+width),length+step+2*deep),outline=BLACK)
        #Now the arcs
        draw.arc((int(width+deep),int(deep),int(2*deep+width),int(2*deep)),270,360,fill="#000000")
        draw.arc((int(width+deep),int(length+deep),int(2*deep+width),int(length+2*deep)),0,90,fill="#000000")
        draw.arc((0,int(deep),int(deep),int(2*deep)),180,270,fill="#000000")
        draw.arc((0,int(length+deep),int(deep),int(length+2*deep)),90,180,fill="#000000")
        ##
        draw.arc((int(deep),0,int(deep+width/2),int(deep)),180,270,fill="#000000")
        draw.arc((int(deep),int(2*deep+length),int(deep+width/2),int(3*deep+length)),90,180,fill="#000000")
        draw.arc((int(width/2+deep),0,int(deep+width),int(deep)),270,360,fill="#000000")
        draw.arc((int(width/2+deep),int(2*deep+length),int(deep+width),int(3*deep+length)),0,90,fill="#0000ff")
        
        #Now copy & resize images in the tuckboxes
        length=int(length)
        width=int(width)
        deep=int(deep)
        step=int(step)
        if front:
            front_image=Image.open(front)
            front_image=front_image.resize((width,length))
            sheet.paste(front_image,(width+2*deep,deep+2*step))
        if back:
            back_image=Image.open(back)
            back_image=back_image.resize((width,length))
            sheet.paste(back_image,(deep,deep+2*step))
        if sidelr:
            side=Image.open(sidelr)
            side=side.resize((length,deep))
            lside=side.rotate(90,expand=True)
            rside=side.rotate(270,expand=True)
            sheet.paste(rside,(0,deep+step*2))
            sheet.paste(lside,(deep+width,deep+2*step))
        if sidetb:
            side=Image.open(sidetb)
            side=side.resize((width,deep))
            bside=side.rotate(180,expand=True)
            sheet.paste(side,(deep,2*step))
            sheet.paste(bside,(deep,length+deep+2*step))
        #Save & display
        sheet.save(dst)
        import os
        os.startfile(dst)
 
script_tb=TuckBoxScript()
