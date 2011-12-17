from actions import Template, Script
import wx


class TrapezeTemplate(Template):
    name='Trapze Image Template'
    help="Apply a trapeze transform on an image"
    column={
        'Steps':('int',100),
        'Delta in %':('int',50),
    } 
    
    def process(self,dc,values):
        #Save bmp and 
        Delta=values['Delta in %']
        Steps=values['Steps']
        bmp=dc.GetAsBitmap()
        img=wx.ImageFromBitmap(bmp)
        W=float(bmp.Width)
        H=float(bmp.Height)
        #First create a new image being Delta larger
        bmp=wx.EmptyBitmap(W,H)
        dc.DrawBitmap(bmp,0,0)
        for i in range(Steps):
            rect=wx.Rect(0,int(round(i*H/Steps)),W,int(round(H/Steps)))
            sub=img.GetSubImage(rect)
            sub.Rescale(int(round(W/(1+(1.0+i)*Delta/(Steps*100)))),int(round(H/Steps)))
            new_w=sub.Width
            #print 'Drawing from ', int(round((W-new_w)/2)) , int(round(H*i/Steps))
            dc.DrawBitmap(wx.BitmapFromImage(sub),
                                int(round((W-new_w)/2)),
                                int(round(H*i/Steps))
                                )
        #And now the picture
            

template_trapeze=TrapezeTemplate()        

class HueTemplate(Template):
    name="Hue changer"
    fitting_size=(307,311)
    column={
            'hue':('slider', 0.0),
            'mask':('img',None),
    }
    help="Change the Hue of the image. Apply mask before if it exists"
    def process( self,dc,values):
        hue=float(values['hue'])/100.0
        import wx
        bmp=dc.GetAsBitmap()
        img=wx.ImageFromBitmap(bmp)
        img.RotateHue(hue)        
        dc.DrawBitmap(wx.BitmapFromImage(img),0,0)

template_hue=HueTemplate()

class HueTransformer(Script):
    name="Hue Transformer"
    help="Create Hue transformed copy of current image"
    column={
        "Steps":('int',4),
        "mask":('img',None),
    }
    def run(self,mainframe,values=None):
        from config import card_folder
        from os.path import join,isfile
        path=mainframe.GetCurrentSelectedPath()
        if not path:
            return
        steps=values['Steps']
        _vs={"hue":0.0,"mask":values['mask']}
        for step in range(steps):
            _vs["hue"]=(step)*100/steps
            mainframe.AddCard(cardPath=path,qt=1,template='Hue changer',values=_vs)
            
script_ht=HueTransformer()
