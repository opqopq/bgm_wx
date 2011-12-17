from actions import Template, Script
import wx

class Chips_template(Template):
    name="Chips"
    fitting_size=(307,311)
    column={
            'hue':('slider', 0.0),
    }
    help="Format in to a circle surrounded by a colored chips. With repeated symbol around"
    
    def process( self,dc,values):
        hue=values['hue']
        import wx
        src=dc.GetAsBitmap()
        w,h=dc.GetSizeTuple()
        #Fill dc with blank
        newdc=wx.MemoryDC()
        white=wx.EmptyBitmapRGBA(w,h,255,255,255,0)
        newdc.SelectObject(white)
        newdc.Brush=wx.Brush(wx.NamedColour('white'),wx.SOLID)
        newdc.DrawRectangle(0,0,w,h)
        #First apply chips mask on the pict
        mask=wx.Mask(wx.Bitmap('plugins/chips/chips_mask.png'),wx.NamedColour('white'))
        src.SetMask(mask)
        newdc.DrawBitmap(src,0,0,True)
        #Then apply chip border on the pict
        img=wx.Image('plugins/chips/chips_border.png')
        img.RotateHue(hue)
        bmp=wx.BitmapFromImage(img)
        #bmp=wx.Bitmap('plugins/chips/chips_border.png')
        mask=wx.Mask(wx.Bitmap('plugins/chips/chips_border_mask.png'),wx.NamedColour('white'))
        bmp.SetMask(mask)
        newdc.DrawBitmap(bmp,0,0,True)
        newdc.SelectObject(wx.NullBitmap)
        del newdc
        #Now, clear the old one & paste the modified bitmap
        dc.Clear()
        #dc.SetBrush(wx.Brush(wx.NamedColour('white'),wx.SOLID))
        #dc.DrawRectangle(0,0,w,h)
        #dc.DrawBitmap(white),0,0)
        dc.DrawBitmap(wx.BitmapFromImage(white.ConvertToImage()),0,0)

        
template_chips=Chips_template()

class Chips_script(Script):
    name="gambit_game_creator"
    #This is required to import the template in the class scope. Otherwise, name error
    def run(self,mainframe,values):
        from config import card_folder
        from os.path import join,isfile
        from math import sqrt
        self.mainframe.GetCurrentSelectedPath()
        for c in ['blue','red','green','yellow','purple']:
            for i in [2,2,3,4,5,6,6]:
                template="gambit_card"
                values={'color':c,'value':i}
                # if cardpath is none=> current card selected
                mainframe.AddCard(cardPath=path,qt=1, template=template,values=values)

script_gambit=Chips_script()