from actions import Template, Script
import wx

class PolygonTemplate(Template):
    name="Polygon Maker"
    help="Create the biggest polygon, rotated by angle. Star mode create stars"
    column={
            'Faces':('int',4),
            'Strike':('color', 'black'),
            'Fill':('bool', False),
            'width':('int',10),
            'Star':('bool',False),
            'Angle':('int',0),
            'Scale':('float',1.0)
            #~ 'font':('font',wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)),
            #~ 'color':('color','black'),
    }	
    def process(self,dc,values):
        from math import cos, sin, radians,pi
        faces=values['Faces']
        color=values['Strike']
        width=values['width']
        fill=values['Fill']
        star_mode=values['Star']
        angle=radians(values['Angle'])
        scale=values['Scale']
        oldbrush=dc.Brush
        if fill:
            #Set a brush if necessary
            dc.SetBrush(wx.Brush(color,wx.SOLID))
        else:
            dc.SetBrush(wx.Brush(color,wx.TRANSPARENT))
        if faces<3:
            print 'Unable to proceed below 3 faces'
            faces=3
        w,h=dc.GetSizeTuple()
        if h<w:
            mode='h'
            minimum=h
        else:
            mode='w'
            minimum=w
        minimum/=2
        pen=dc.Pen
        dc.SetPen(wx.Pen(color,width,wx.SOLID))
        points=[]
        center=wx.Point(0,0)
        for i in range(faces):
            points.append(wx.Point(scale*minimum*cos(i*2*pi/faces + angle),scale*minimum*sin(i*2*pi/faces + angle)))
            if star_mode:
                points.append(center)
        dc.DrawPolygon(points,w/2,h/2)
        dc.SetPen(pen)
        dc.SetBrush(oldbrush)
        
template_polygon=PolygonTemplate()

class CircleTemplate(Template):
    name="Circle Maker"
    help="Create the biggest circle"
    column={
            'Strike':('color', 'black'),
            'Fill':('bool', False),
            'width':('int',10),
            'scale':('float',1.0),
    }	
    def process(self,dc,values):
        from math import cos, sin, radians,pi
        color=values['Strike']
        width=values['width']
        fill=values['Fill']
        scale=values['scale']
        oldbrush=dc.Brush
        if fill:
            #Set a brush if necessary
            dc.SetBrush(wx.Brush(color,wx.SOLID))
        else:
            dc.SetBrush(wx.Brush(color,wx.TRANSPARENT))
        w,h=dc.GetSizeTuple()
        if h<w:
            mode='h'
            minimum=h
        else:
            mode='w'
            minimum=w
        minimum/=2
        minimum*=scale
        pen=dc.Pen
        dc.SetPen(wx.Pen(color,width,wx.SOLID))
        center=wx.Point(0,0)
        dc.DrawCircle(w/2,h/2,minimum)
        dc.SetPen(pen)
        dc.SetBrush(oldbrush)
        
template_circle=CircleTemplate()
    
class PolygonMask(Template):
    name="Polygon Mask Maker"
    help="Crop the current picture in the biggest polygon, rotated by angle."
    column={
            'Faces':('int',4),
            #'Strike':('color', 'black'),
            #'Fill':('bool', False),
            #'width':('int',10),
            #'Star':('bool',False),
            'Angle':('int',0),
            'Scale':('float',1.0)
            #~ 'font':('font',wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)),
            #~ 'color':('color','black'),
    }	
    def process(self,dc,values):
        from math import cos, sin, radians,pi
        olddc=dc
        w,h=olddc.GetSizeTuple()
        faces=values['Faces']
        color=wx.NamedColour('black')
        width=1#values['width']
        fill=True#values['Fill']
        angle=radians(values['Angle'])
        scale=values['Scale']
        dc=wx.MemoryDC()
        white=wx.EmptyBitmapRGBA(w,h,255,255,255,0)
        dc.SelectObject(white)
        #Fill with white
        dc.SetBrush(wx.Brush(wx.NamedColour('white'),wx.SOLID))
        dc.DrawRectangle(0,0,w,h)
        if faces<3:
            print 'Unable to proceed below 3 faces'
            faces=3
        minimum=min(h,w)/2
        dc.SetBrush(wx.Brush(color,wx.SOLID))
        points=[]
        center=wx.Point(0,0)
        for i in range(faces):
            points.append(wx.Point(scale*minimum*cos(i*2*pi/faces + angle),scale*minimum*sin(i*2*pi/faces + angle)))
        dc.DrawPolygon(points,w/2,h/2)
        #Done with the drawing.
        dc.SelectObject(wx.NullBitmap)
        mask=wx.Mask(white,wx.NamedColour('white'))
        bmp=olddc.GetAsBitmap()
        bmp.SetMask(mask)
        dc=olddc
        dc.SetBrush(wx.Brush(wx.NamedColour('white'),wx.SOLID))
        dc.DrawRectangle(0,0,w,h)
        dc.DrawBitmap(bmp,0,0,True)
        #~ olddc.SetPen(wx.NullPen)
        #~ olddc.SetBrush(wx.NullBrush)
        #~ del dc
        
template_polygon_mask=PolygonMask()
    
    
class CircleMask(Template):
    name="Circle Mask Maker"
    help="Crop the current picture in the biggest circle."
    column={
            'Scale':('float',1.0)
    }	
    def process(self,dc,values):
        from math import cos, sin, radians,pi
        olddc=dc
        w,h=olddc.GetSizeTuple()
        width=1#values['width']
        fill=True#values['Fill']
        scale=values['Scale']
        dc=wx.MemoryDC()
        white=wx.EmptyBitmapRGBA(w,h,255,255,255,0)
        dc.SelectObject(white)
        #Fill with white
        dc.SetBrush(wx.Brush(wx.NamedColour('white'),wx.SOLID))
        dc.DrawRectangle(0,0,w,h)
        minimum=min(h,w)/2
        minimum*=scale
        dc.SetBrush(wx.Brush("black",wx.SOLID))
        dc.DrawCircle(w/2,h/2,minimum)
        #Done with the drawing.
        dc.SelectObject(wx.NullBitmap)
        mask=wx.Mask(white,wx.NamedColour('white'))
        bmp=olddc.GetAsBitmap()
        bmp.SetMask(mask)
        dc=olddc
        dc.SetBrush(wx.Brush(wx.NamedColour('white'),wx.SOLID))
        dc.DrawRectangle(0,0,w,h)
        dc.DrawBitmap(bmp,0,0,True)
        #~ olddc.SetPen(wx.NullPen)
        #~ olddc.SetBrush(wx.NullBrush)
        #~ del dc
        
template_circle_mask=CircleMask()
    