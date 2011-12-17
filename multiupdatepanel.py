"Define a simple panel used for chossing what to update"

import wx

skip=['Name','Path','Values']

class MultiUpdatePanel(wx.Dialog):
        def __init__(self,parent,newCard,oldCard):
            self.newCard=newCard
            self.oldCard=oldCard
            if newCard.Values:
                size=(600,350+max(0,20*(len(newCard.Values)-5)))
            else:
                size=(250,350)
            wx.Dialog.__init__(self,parent,size=size,style=wx.DEFAULT_DIALOG_STYLE)
            self.Title="Multi Update Panel"
            self.Sizer=wx.BoxSizer(wx.VERTICAL)
            self.Sizer.Add(wx.StaticText(self,-1,'Choose what you want to update.'),0,wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,15)
            thebox=wx.BoxSizer()
            self.Sizer.Add(thebox, 1, wx.EXPAND|wx.ALL, 25)
            self.cardoptions=[]
            self.templateoptions=[]
            #Format options
            box = wx.StaticBox(self, -1, "Format Options:")
            bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)
            from deckmvc import columns
            #all ones
            w=wx.CheckBox(self,-1,"All card Options")
            bsizer.Add(w,0,wx.ALL,10)
            w.Bind(wx.EVT_CHECKBOX,self.OnCardOptionsCheck)
            w.Value=True
            for label in columns:
                if label in skip:
                    continue
                w=wx.CheckBox(self,-1,"%s to '%s'"%(label,getattr(newCard,label)))
                w._label=label
                w.Value=True
                bsizer.Add(w,0,wx.TOP| wx.LEFT|wx.DOWN ,2)
                self.cardoptions.append(w)
            thebox.Add(bsizer, 1, wx.EXPAND|wx.ALL, 10)
            #Template option
            if newCard.Values:
                box2 = wx.StaticBox(self, -1, "Template Options:")
                bsizer2 = wx.StaticBoxSizer(box2, wx.VERTICAL)
                w=wx.CheckBox(self,-1,"All card Options")
                bsizer2.Add(w,0,wx.ALL,10)
                w.Bind(wx.EVT_CHECKBOX,self.OnTemplateOptionsCheck)
                w.Value=True
                for label,value in newCard.Values.items():
                    w=wx.CheckBox(self,-1,"%s from %s to '%s'"%(label,oldCard.Values.get(label,'N/A'),value))
                    w._label=label
                    bsizer2.Add(w,0,wx.TOP| wx.LEFT|wx.DOWN ,2)
                    w.Value=True
                    self.templateoptions.append(w)
                thebox.Add(bsizer2, 1, wx.EXPAND|wx.ALL, 10)
            #Action button
            hbox=wx.BoxSizer()
            ok=wx.Button(self,-1,'OK')
            ko=wx.Button(self,-1,'Cancel')
            ko.Bind(wx.EVT_BUTTON,self.OnCancel)
            ok.Bind(wx.EVT_BUTTON,self.OnApply)
            hbox.Add(ok,0,wx.ALIGN_CENTER_VERTICAL,0)
            hbox.Add(ko,0,wx.ALIGN_CENTER_VERTICAL,0)
            self.Sizer.Add(hbox,0,wx.ALIGN_CENTER_HORIZONTAL|wx.ALL,10)
            ok.SetFocus()            
            self.Show()
            
            
        def OnCardOptionsCheck(self,evt):
            for w in self.cardoptions:
                w.Value=evt.IsChecked()
            
        def OnTemplateOptionsCheck(self,evt):
            for w in self.templateoptions:
                w.Value=evt.IsChecked()
            
        def OnCancel(self,evt):
            self.Destroy()
            
        def OnApply(self,evt):
            data=dict()
            _cfilter=[w._label for w in self.cardoptions if w.Value]
            _tfilter=[w._label for w in self.templateoptions if w.Value]
            self.Parent.deckgrid.MultiUpdate(self.newCard,_cfilter=_cfilter,_tfilter=_tfilter)
            self.Destroy()

