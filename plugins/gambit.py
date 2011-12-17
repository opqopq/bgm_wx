from actions import Template, Script
import wx


class Gambit_template(Template):
    name="gambit_card"
    column={
            'color':('color','red'),
            'value':('str','343'),
    }
    help="Draw some Text centered at its maximum font size"
    
    def process( self,dc,values):
        #print values
        color=values['color']
        val=values['value']
        import wx
        font1 = wx.Font(30, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Comic Sans MS')
        dc.Font=font1
        #print color, type(color)
        dc.TextForeground=color
        h,w=dc.GetSizeTuple()
        eh,ew=dc.GetTextExtent(str(val))
        #print h,eh, w,ew, h>eh, w>ew, h>eh and w>ew
        while  h>eh and w>ew:
            font1.SetPointSize(font1.GetPointSize()*2)
            dc.Font=font1
            eh,ew=dc.GetTextExtent(str(val))
        font1.SetPointSize(font1.GetPointSize()/2)
        dc.Font=font1
        eh,ew=dc.GetTextExtent(str(val))
        #print 'size',dc.GetSizeTuple(),'extent', dc.GetTextExtent(str(val)), 'font', dc.Font.PointSize, dc.Font.PixelSize
        dc.DrawText(str(val),(h-eh)/2,(w-ew)/2)

class Gambit_script(Script):
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

script_gambit=Gambit_script()
template_gambit=Gambit_template()
