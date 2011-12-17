from actions import Template, Script
import wx
from wx.lib.wordwrap import wordwrap

class CodeSevenQuestionTemplate(Template):
    name="Code 777 Question"
    help="Create 777 Question Card"
    
    column={
    "num":('int',1),
    "question":('str','How are you ?')
    }
    
    def process( self,dc,values):
         from wx.lib.wordwrap import wordwrap
         dc.Font=wx.Font(48, wx.SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD, False, u'Comic Sans MS')
         dc.TextForeground='white'
         w,h=dc.GetSizeTuple()
         stepw,steph=int(0.1*w),int(0.1*h)
         dc.DrawText('#%2d'%values['num'],3*stepw,3*steph)
         wrapped_text=wordwrap(values['question'], 8*stepw, dc, breakLongWords=True, margin=0)
         if dc.CharHeight*len(wrapped_text.splitlines())>8*steph:
             print 'Houstin, we have a souci-> reduce font size'
         for i,line in enumerate(wrapped_text.splitlines()):
             dc.DrawText(line.strip(),stepw,4*steph + i*dc.CharHeight)
         
template_777=CodeSevenQuestionTemplate()

class CodeSevenScript(Script):
    name="Code 777 Game Maker"
    help="Create for Code 777 Game, based on selected image as background"
    def run(self,mainframe,values=None):
        from config import card_folder
        from os.path import join,isfile
        path=mainframe.GetCurrentSelectedPath()
        qts=[1,2,3,4,4,1,3,3,1,2,4]
        colors=['green','yellow','black','brown','red','black','green','pink','pink','yellow','blue']
        values=[1,2,3,4,5,5,6,6,7,7,7]
        for qt,col,val in zip(qts,colors,values):
            _vs={'color':col,'value':val,}
            mainframe.AddCard(cardPath=path, qt=qt, template='gambit_card', values=_vs )
        
script_code=CodeSevenScript()
    