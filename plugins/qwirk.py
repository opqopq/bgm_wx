from actions import Template, Script
import wx


class QwirkScript(Script):
    name="Qwirk Game Maker"
    help="Create Elements for Qwirk, based on selected image as background"
    column={
        "Length (in cm)":('int',4)
    }
    def run(self,mainframe,values=None):
        from config import card_folder
        from os.path import join,isfile
        from math import sqrt
        w=h=size_length=int(values['Length (in cm)'] * 118.1)
        path=mainframe.GetCurrentSelectedPath()
        if not path:
            return
        init_vals={
            'Faces':4,
            'Strike':'black',
            'Fill': True,
            'Star':False,
        }
        for color in ['red','white','yellow','green','blue','purple']:
            for star, angle,faces in zip([0,1,0,0,0,0],[0,45,0,45,30,30],[360,4,4,4,6,3]):
                _vs=init_vals.copy()
                _vs['Strike']=color
                _vs['Star']=bool(star)
                _vs['Angle']=angle
                _vs['Faces']=faces
                mainframe.AddCard(
                                    cardPath=path,
                                    qt=3,
                                    template=mainframe.templates['plugins/polygon.py'].name,
                                    values=_vs                                
                            )

        mainframe.fitting_size=(w,h)
        mainframe.fit.Value="%sx%s"%(w,h)
        
script_qwirk=QwirkScript()
    