from actions import Template, Script
import wx


class OrigamiDiceTemplate(Template):
    name='Origami Dice Template'
    help="Turn given image in a face of origami dice"
    column={} 
    
    def process(self,dc,values):
        from math import radians, sqrt
        #Save bmp and rescale it as the dice arry
        bmp=dc.GetAsBitmap()
        w,h=bmp.GetSize()
        size_length=w/(2*sqrt(2))
        img=wx.ImageFromBitmap(bmp)
        img.Rescale(size_length, size_length)
        #Paste the rotated bmp
        dc.Clear()
        #Draw the necessary lines
        dc.Pen=wx.Pen('black')
        b=size_length
        c=float(b)*sqrt(2)/2
        #Partial diagonal lines
        dc.DrawLine(0,c,2*c,3*c)
        dc.DrawLine(c,4*c,3*c,2*c)
        dc.DrawLine(4*c,3*c,2*c,c)
        dc.DrawLine(3*c,0,c,2*c)
        #Straing lines
        dc.DrawLine(0,c,2*c,c)
        dc.DrawLine(2*c,3*c,4*c,3*c)
        #And now the picture
        gc=wx.GraphicsContext_Create(dc)
        gc.Translate(2*c,c)
        gc.Rotate(radians(45))
        gc.DrawBitmap(wx.BitmapFromImage(img),0,0,b,b)

template_origami=OrigamiDiceTemplate()        

class OrigamiScript(Script):
    name="Origami dice Maker"
    help="Create fit size  based on a dice face. Optionnaly, split the selected image in six"
    column={
        'Dice Length (in cm)':('float',2.0),
        'Split Selected Image?':('bool',False),
    }
    def run(self,mainframe,values=None):
        from config import card_folder
        from os.path import join,isfile
        from math import sqrt
        if not values:
            size_length=2*118.1
            split=False
        else:
            size_length=values['Dice Length (in cm)'] * 118.1
            split=values['Split Selected Image?']
        if split:
            #Take the selected image, split in 6 in order to obtain 6 squares           
            path=mainframe.GetCurrentSelectedPath()
            if not path:
                return
            img=wx.Image(join(card_folder.decode('cp1252'),path.decode('cp1252')))
            w,h=img.GetWidth(),img.GetHeight()
            w=float(w)
            h=float(h)
            nblines=int(round(6*h/w))
            for j in range(nblines):
                for i in range(6):
                    rect=wx.Rect(i*w/6,j*h/nblines,w/6,h/nblines)
                    simg=img.GetSubImage(rect)
                    #Save the small one
                    simg.SaveFile(join(card_folder.decode('cp1252'),'ori_sub_%d_%d.jpg'%(i,j) ),  wx.BITMAP_TYPE_JPEG)
                    #Add the cards
                    mainframe.AddCard(
                            cardPath="ori_sub_%d_%d.jpg"%(i,j),
                            qt=1,
                            template=mainframe.templates['Origami Dice Template'].name
                    )

        w=h=int(sqrt(2) * 2 * size_length)
        mainframe.fitting_size=(w,h)
        mainframe.fit.Value="%sx%s"%(w,h)
        
script_origami=OrigamiScript()
