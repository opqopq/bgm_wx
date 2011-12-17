from actions import Template, Script
import wx

class PentaValueTemplate(Template):
    name="Penta Value"
    help="Write a given Value at the center & on the cardinal point of a card"
    column={
            'value':('str','TXT'),
            'font':('font',wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)),
            'color':('color','black'),
    }
    
    def oprocess(self,dc,values):
        gc = wx.GraphicsContext.Create(dc)
        color=values['color']
        val=values['value']
        font=values['font']
        #dc.TextForeground=color
        h,w=dc.GetSizeTuple()
        #dc.Font=font
        eh,ew=dc.GetTextExtent(str(val))
        gc.SetPen(wx.Pen("navy", 1))
        #gc.SetTextColor('black')
        for i in range(2):
        #Rotate the DC and then print the value in the upper middle
                #gc.DrawText(str(val),(h-eh)/2,0)
                gc.Rotate(90)
        #Now print the value in the middle
        dc.DrawText(str(val),(h-eh)/2,(w-ew)/2)

    def vprocess(self,dc,values):
        val=values['value']
        color=values['color']
        font=values['font']
        ew, eh = dc.GetTextExtent(val)
        for i in range(4):
            #Save as Bitmap
            bmp=dc.GetAsBitmap()
            #Save as Image
            image=wx.ImageFromBitmap(bmp)
            #Rotate Image
            image=image.Rotate90()
            #Create Bitmap rotated
            bmp=wx.BitmapFromImage(image)
            #Create dc
            dc.SelectObject(wx.NullBitmap)
            del dc
            dc=wx.MemoryDC()
            dc.SelectObject(bmp)
            dc.SetFont(font)
            #Draw the text
            h,w=dc.GetSizeTuple()
            dc.DrawText(str(val),(h-eh)/2,0)
        #Now print the value in the middle
        dc.DrawText(str(val),(h-eh)/2,(w-ew)/2)
        #Clear the dc just in case
        bmp=dc.GetAsBitmap()
        dc.SelectObject(wx.NullBitmap)
        del dc
        return bmp
    
    def process(self,dc,values):
        val=values['value']
        color=values['color']
        font=values['font']
        ew, eh = dc.GetTextExtent(val)
        from math import cos, sin, radians
        gc = wx.GraphicsContext.Create(dc)
        gc.SetFont(font)
        gc.SetPen(wx.Pen("navy", 1))
        gc.SetBrush(wx.Brush("pink"))        
        w,h=dc.GetSizeTuple()
        gc.Translate(w/2,h/2)
        a,b=h/2,w/2
        #First, at the Center
        gc.DrawText(val,-ew/2,-eh/2)
        #gc.DrawBitmap(bmp,-d,-c,2*d, 2*c)
        for angle,coords in enumerate([(0,w),(h,0)]):
            _x,_y=coords
            gc.DrawRotatedText(val,_x/2-ew/2,_y/2-eh/2,radians(angle*90))
            gc.DrawRotatedText(val,-(_x/2-ew/2),-(_y/2-eh/2),radians(angle*90)+radians(180))
            a,b=b,a
            gc.Rotate(radians(90))
        
template_penta=PentaValueTemplate()

class FoilTemplate(Template):
    name="Foil Template"
    help="Add a foil layer on top of the image with alpha. Either from given color or given image"
    column={
        'alpha':('int',128),
        'color':('color',wx.Colour()),
        'img': ('img',None),
    }
    
    def process(self,dc,values):
        from widgets import ColorElement, ImgElement
        if values['img']:
            import os.path
            if os.path.isfile(values['img']):
                obj=ImgElement()
                gridvalue=values['img']
            else:
                print "Warning: not existing image %s. Resorting to color"%values['img']
        else:
            obj=ColorElement()
            gridvalue=values['color']
        obj.template=self
        obj['alpha']=values['alpha']
        obj['left']=obj['top']=0
        w,h=dc.GetSizeTuple()
        obj['width']=w
        obj['height']=h       
        obj.Render(gridvalue,dc,self,values)
        
template_foil=FoilTemplate()
    
class MirrorScript(Script):
    "Duplicate all existing cards to add Dual ones right after"
    name="Mirror Maker"
    help="Duplicate all entries as dual ones"
    column={
            'GreyScale Back':('bool',False),

    }
    def run(self,mainframe,values=None):
        from config import card_folder
        from os.path import join,isfile
        from deckmvc import columns
        dogrey=values['GreyScale Back']
        dc=mainframe.deckgrid
        for i in range(dc.numrow):
            [displayName,qt,cardPath,fsize,dual,rotated,template,_vs]=[dc.GetValue(i,j) for j in range(len(columns))]            
            if dogrey:
                template="GreyScale Template"
            mainframe.AddCard(cardPath=cardPath,qt=qt,template=template,values=_vs,displayName=displayName,dual=True,rotated=rotated,fitting_size=fsize)
        mainframe.updateinfo(data=[])
    
script_mirror=MirrorScript()
    
    
    