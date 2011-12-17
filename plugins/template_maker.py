from actions import Script
#Load Definition for yaml element in yaml library

class TemplateMaker(Script):
    help="Create Simple Text Template"
    name="Template Designer"
    column={
        'File': ('file',''),
        'version':('float',1.0),
    }    
    
    def run(self,mainframe,values=None):
        from designer import WYSIFrame
        mini= WYSIFrame(mainframe)
        mini.Show()
    
script_templatemaker=TemplateMaker()


        