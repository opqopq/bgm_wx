from actions import Template, Script, template_empty
import wx


class Border_template(Template):
    name='Border Template'
    column={'color_out':('color','black'),
            'color_in':('color','white'),
            'width':('int',30),
            'radius':('int',40),
            'offset':('int',10),
            'extension':('bool',False)
    }
    help="Draw Rounded Rectangle"
    
    def process ( self ,dc,values):
        import wx
        width=values['width']
        radius=values['radius']
        extension=values['extension']
        offset=values['offset']
        if extension:
            #reduce the picture of width pixel
            bmp=dc.GetAsBitmap()
            img=wx.ImageFromBitmap(bmp)
            s=img.GetSize()
            w,h=s.width,s.height
            img.Rescale(w-2*width,h-2*width)
            bmp=wx.BitmapFromImage(img)
            dc.Clear()
            dc.DrawBitmap(bmp,width,width)
        h,w=dc.GetSize()
        dc.SetBrush(wx.Brush(wx.CYAN, wx.TRANSPARENT))
        #First a large inside one
        dc.SetPen(wx.Pen(values['color_in'],values['width']+5,wx.SOLID))
        dc.DrawRoundedRectangle(offset,offset,h-2*offset,w-2*offset,radius)         
        #Then a smaller white one, above
        dc.SetPen(wx.Pen(values['color_out'],width,wx.SOLID))
        dc.DrawRoundedRectangle(0,0,h,w,values['radius'])

template_rounded_border=Border_template()

class SplitterScript(Script):
    "Take the selected pictures and split according to current fittingg size"
    name="Board Split Maker"
    help="Create fit size card by splitting selected image. Optionnaly, try to scale it as little as possible"
    column={
        'Try to Rescale ?':('bool',False),
    }
    def run(self,mainframe,values=None):
        from config import card_folder
        from os.path import join,isfile
        from math import ceil
        rescale=values['Try to Rescale ?']
        path=mainframe.GetCurrentSelectedPath()
        if not path:
            return
        img=wx.Image(join(card_folder.decode('cp1252'),path.decode('cp1252')))
        w,h=float(img.GetWidth()),float(img.GetHeight())
        fw,fh=mainframe.fitting_size
        width_ratio=w/fw
        height_ratio=h/fh
        if rescale:
            width_ratio=int(round(width_ratio))
            height_ratio=int(round(height_ratio))
            #If one size is smaller tahn the fitting size, take fitting size as minimum
            if width_ratio==0:width_ratio=1
            if height_ratio==0:height_ratio=1
            img=img.Rescale(fw*width_ratio,fh*height_ratio)
        else:
            width_ratio=int(ceil(width_ratio))
            height_ratio=int(ceil(height_ratio))
        for wr in range(width_ratio):
            for hr in range(height_ratio):
                rect=wx.Rect(wr*fw,hr*fh,min(fw,w-wr*fw),min(fh,h-hr*fh))
                simg=img.GetSubImage(rect)
                #Save the small one
                simg.SaveFile(join(card_folder.decode('cp1252'),'split_%d_%d.jpg'%(wr,hr)),wx.BITMAP_TYPE_JPEG)
                #Add the cards
                mainframe.AddCard(cardPath='split_%d_%d.jpg'%(wr,hr),qt=1)
    
script_splitter=SplitterScript()

class SubSplitFormat(Template):
    name='Subsplit Template'
    column={
            'x0':('str','0'),
            'y0':('str','0'),
            'x1':('str','100'),
            'y1':('str','100'),
    }
    help="Take given Rectangle as subscript"
    
    def process ( self ,dc,values):
        import wx
        bmp=dc.GetAsBitmap()
        img=wx.ImageFromBitmap(bmp)
        w,h=img.GetSize().Get()
        
        #now with bdirect image cropping
        from config import card_folder
        from os.path import join,isfile
        from __main__ import  frame as mainframe
        path=mainframe.GetCurrentSelectedPath()        
        if not path:
            return
        img=wx.Image(join(card_folder.decode('cp1252'),path.decode('cp1252')))
        w,h=float(img.GetWidth()),float(img.GetHeight())
                
        def check(x,value=None):
            if x.endswith('%'):
                return value* int(x[:-1])/100
            else:
                return int(x)
        x0=check(values['x0'],w)
        y0=check(values['y0'],h)
        x1=check(values['x1'],w)
        y1=check(values['y1'],h)
        rect=wx.Rect(x0,y0,min(w,x1-x0),min(h,y1-y0))
        simg=img.GetSubImage(rect)
        
        simg.Rescale(*dc.GetSizeTuple())
        bmp=wx.BitmapFromImage(simg)
        dc.DrawBitmap(bmp,0,0)
    
template_sub=SubSplitFormat()

class SubSplitScript(Script):
    help="Create col*row stub with proper part "
    name="SubImage Maker"
    column={
        'Num Row':('int',3),
        'Num Col':('int',3),
        'Save as percentage ?':('bool',True),

    }
    def run(self,mainframe,values=None):
        from config import card_folder
        from os.path import join,isfile
        path=mainframe.GetCurrentSelectedPath()        
        if not path:
            return
        img=wx.Image(join(card_folder.decode('cp1252'),path.decode('cp1252')))
        w,h=float(img.GetWidth()),float(img.GetHeight())
        #Keep the old fitting size
        fw,fh=mainframe.fitting_size
        #I know this is mestup ! do not want to dfix it now
        numcol=values['Num Row']
        numrow=values['Num Col']
        percentage=values['Save as percentage ?']
        fw,fh=mainframe.fitting_size
        ending=''
        if percentage:
            fw,fh=100,100
            ending='%'
        stepw=fh/numcol
        steph=fw/numrow
        for j in range(numcol):
            for i in range(numrow):
                _vs={'x0':str(i*steph)+ending,'y0':str(j*stepw)+ending,'x1':str((i+1)*steph)+ending,'y1':str((j+1)*stepw)+ending}
                mainframe.AddCard(cardPath=path,qt=1,template='Subsplit Template',values=_vs)
    
script_sub=SubSplitScript()

class BW_template(Template):
    name='GreyScale Template'
    column={}
    help="Convert Picture to Greyscale"
    
    def process ( self ,dc,values):
        import wx
        bmp=dc.GetAsBitmap()
        img=wx.ImageFromBitmap(bmp)
        img=img.ConvertToGreyscale()
        bmp=wx.BitmapFromImage(img)
        dc.DrawBitmap(bmp,0,0)        

template_greyscale=BW_template()
