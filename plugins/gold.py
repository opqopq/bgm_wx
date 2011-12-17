from actions import Template, Script
import wx

class GoldTemplate(Template):
    name="Gold Template"
    help="Template for Gold Game Cards"
    column={
            'value':('int',2),
            'color':('color', 'black'),
    }	
    def process(self,dc,values):
        from math import cos, sin, radians,pi
        value=values['value']
        color=values['color']
        dc.SetBrush(wx.Brush(color,wx.SOLID))
        w,h=dc.GetSizeTuple()
        width=int(0.05*w)
        pen=dc.Pen
        dc.Font=wx.Font(48, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Comic Sans MS')
        dc.SetPen(wx.Pen(color,width,wx.SOLID))
        stepw,steph=int(0.1*w),int(0.1*h)
        #The Four borders
        points=[]
        points.append(wx.Point(stepw,steph))
        points.append(wx.Point(9*stepw,steph))
        points.append(wx.Point(9*stepw,9*steph))
        points.append(wx.Point(stepw,9*steph))
        points.append(wx.Point(stepw,steph))
        dc.DrawLines(points)
        #The four circles
        points.pop()
        for point in points:
            dc.DrawCirclePoint(point,min(steph/2,stepw/2))
            dc.DrawTextPoint(str(value),point)
        #The Gold back at the center & the value, in big, at the center
        dc.DrawText(str(value),w/2,h/2)
        #The Value, in all center
        dc.SetPen(pen)

        
template_gold=GoldTemplate()

class GoldScript(Script):
    name="Gold Game Maker"
    help="Create Elements for Gold, based on selected image as background"
    column={
    }
    def run(self,mainframe,values=None):
        from config import card_folder
        from os.path import join,isfile
        from math import sqrt
        path=mainframe.GetCurrentSelectedPath()
        if not path:
            return
        _vs=dict()
        for color in ['red','pink','yellow','green','blue','purple']:
            for value in [3,3,4,5,6,7,8]:
                _vs['value']=value
                _vs['color']=color
                mainframe.AddCard(
                                    cardPath=path,
                                    qt=1,
                                    template='Gold Template',
                                    values=_vs                                
                            )


        
script_gold=GoldScript()
    