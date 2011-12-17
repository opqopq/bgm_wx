#!/usr/bin/env python
import os
import sys
import wx
sys.defaultencoding='cp1252'

todos=[
    '[P1]: add a way to conpound templates',
    '[P3]: add a script for pasting several hex next to each other',
    '[P3]: Add a config frame with all bgm.ini option',
    '[P3]: add shadow to text element',
    '[P1]: replace cache mcasnism for template: add an option for force reload in get or getitem in templatedirectory',
    '[P2]: replace image progrid loader to have mask feature & cropping / resize feature like MSE',
    '[P2]: find a way to distingate between game/style property and new property',

]

for t in todos:
    print "[BGM]:",t
    
from mainFrame import MainFrame

if __name__ == '__main__':
        app = wx.PySimpleApp()
        wx.InitAllImageHandlers()
        frame = MainFrame(None)
        START=True
        if '--debug' in sys.argv:
            frame.OnPyShell(None)
            sys.argv.remove('--debug')
        if len(sys.argv)>1 :#filename of a deck ?? load it ! 
            name=sys.argv[1]
            if name.endswith('.dck') or name.endswith('.csv'):
                print 'Loading Deck ',name
                frame.LoadDeck(sys.argv[1])
            elif name.endswith('.py') or name.endswith('.tmpl') or name.endswith('bgp') :
                print 'Loading Script/Template',name
                #This fire the callback =>load the file
                frame.LoadTemplate(name,select=True)
        if '--print' in sys.argv:
            START=False
            print 'Start formatting....',
            frame.OnEditmenuIdprintMenu(None)
            print 'Done.'
        if '--batchprint' in sys.argv:
            START=False
            sys.argv.remove('--batchprint')
            ZOOM=False
            if '--fitfactor' in sys.argv:
                index=sys.argv.index('--fitfactor')
                wfactor,hfactor=sys.argv[index+1:index+3]
                for i in range(3):del sys.argv[index]
                ZOOM=True
            import printer
            from glob import glob
            dir="tmp"
            for _x in sys.argv[1:]:
                for x in glob(_x):
                    if x.startswith('--'):
                        continue
                    print 'Printing ',x
                    frame.LoadDeck(x)
                    fs=frame.fitting_size
                    if ZOOM:
                        fs=[int(float(wfactor)*fs[0]),int(float(hfactor)*fs[1])]
                    printer.format(frame.GetCurrentDeck(),dir,frame.deckname,fitting_size=fs,templates=frame.templates)
            import os
            if hasattr(os,'startfile'):
                os.startfile(dir)
        if START:
            frame.Show()
            app.MainLoop()