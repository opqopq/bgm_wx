import wx
import wx.lib.agw.pycollapsiblepane as PCP


class FitSizeDialog(wx.Dialog):
    def __init__(self,parent):
        wx.Dialog.__init__(self,parent,-1,'Card Fitting Size',size=wx.Size(0,0),style=wx.DEFAULT_DIALOG_STYLE)
        self.zoom=2
        self.aspect=True
        self.Sizer=wx.BoxSizer(wx.VERTICAL)
        sz=self.Sizer
        #First, height & width
        #Height
        plus_size=wx.Size(20,20)
        ws=wx.BoxSizer()
        ws.Add(wx.StaticText(self,-1,"Width:"),1,0,2)
        self.WidthText=wx.TextCtrl(self,-1)
        self.WZButton=wx.Button(self,-1,'*', size=plus_size)
        self.sWZButton=wx.Button(self,-1,'/', size=plus_size)
        ws.Add(self.WidthText,1,0,2)
        ws.Add(self.WZButton)
        ws.Add(self.sWZButton)
        sz.Add(ws,0,wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        #Height
        hs=wx.BoxSizer()
        hs.Add(wx.StaticText(self,-1,"Height:"),1,0,2)
        self.HeightText=wx.TextCtrl(self,-1)
        self.HZButton=wx.Button(self,-1,'*',size=plus_size)
        self.sHZButton=wx.Button(self,-1,'/',size=plus_size)
        hs.Add(self.HeightText,1,0,2)
        hs.Add(self.HZButton)
        hs.Add(self.sHZButton)
        sz.Add(hs,0,wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        #Options
        collpane = PCP.PyCollapsiblePane(self, -1, "Options:",agwStyle=PCP.CP_GTK_EXPANDER)
        # add the pane with a zero proportion value to the 'sz' sizer which contains it
        sz.Add(collpane, 0, wx.GROW|wx.ALL, 5)
        # now add a test label in the collapsible pane using a sizer to layout it:
        win = collpane.GetPane()
        paneSz = wx.BoxSizer(wx.VERTICAL)
        #Zoom factor
        zs=wx.BoxSizer()
        self.ZoomText=wx.SpinCtrl(win, -1, size=wx.Size(100,20))
        #sc.SetRange(1,100)
        self.ZoomText.SetValue(2)
        zs.Add(wx.StaticText(win, -1, "Zoom"), 1, 0, 2)
        zs.Add(self.ZoomText, 1, wx.ALIGN_LEFT, 2)
        paneSz.Add(zs,0,wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        #Aspect Ration factor
        ps=wx.BoxSizer()
        self.AspectRatio=wx.CheckBox(win,-1,'Preserved')
        self.AspectRatio.Value=True
        ps.Add(wx.StaticText(win, -1, "Aspect Ratio"), 1, wx.GROW|wx.ALL, 2)
        ps.Add(self.AspectRatio, 1, wx.GROW|wx.ALL, 2)
        paneSz.Add(ps,0,wx.ALIGN_CENTER_VERTICAL|wx.ALL,5)
        #Unit Radio
        units=wx.RadioBox(win, -1, "Units:", wx.DefaultPosition, wx.DefaultSize,['pixel','cm'], 2, wx.RA_SPECIFY_COLS)
        paneSz.Add(units, 1, wx.ALIGN_CENTER_VERTICAL|wx.GROW|wx.ALL, 5)
        win.SetSizer(paneSz)
        paneSz.SetSizeHints(win)
        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sz.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()        
        btn = wx.Button(self, wx.ID_OK)

        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)

        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sz.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5)

        sz.Fit(self)
        #Callback
        self.HeightText.Bind(wx.EVT_TEXT,self.OnHeightChange)
        self.WidthText.Bind(wx.EVT_TEXT,self.OnWidthChange)
        self.HZButton.Bind(wx.EVT_BUTTON,self.OnHZoom)
        self.WZButton.Bind(wx.EVT_BUTTON,self.OnWZoom)
        self.sHZButton.Bind(wx.EVT_BUTTON,self.OnsHZoom)
        self.sWZButton.Bind(wx.EVT_BUTTON,self.OnsWZoom)
        units.Bind(wx.EVT_RADIOBOX,self.OnUnitChange)
        self.units=units
        #Hidden aspect ratio default value
        self._ar=1
        
        
    def OnUnitChange(self,event):
        print 'On Unit change clicked. to be impleted'
        
    def OnHeightChange(self,evt):
        if self.AspectRatio.Value:
            self.WidthText.ChangeValue(str(int(self._ar*float(self.HeightText.Value))))

    def OnWidthChange(self,evt):
        if self.AspectRatio.Value:
            self.HeightText.ChangeValue(str(int(float(self.WidthText.Value)//self._ar)))
 
    def OnHZoom(self,evt):
        self.HeightText.Value=str(int(float(self.HeightText.Value)*float(self.ZoomText.Value)))
        
    def OnWZoom(self,evt):
        self.WidthText.Value=str(int(float(self.WidthText.Value)*float(self.ZoomText.Value)))

    def OnsHZoom(self,evt):
        self.HeightText.Value=str(int(float(self.HeightText.Value)/float(self.ZoomText.Value)))
        
    def OnsWZoom(self,evt):
        self.WidthText.Value=str(int(float(self.WidthText.Value)/float(self.ZoomText.Value)))
    
    def SetValues(self,fitting_size):
        w,h=fitting_size
        self.WidthText.ChangeValue(str(w))
        self.HeightText.ChangeValue(str(h))
        self._ar=float(w)/float(h)
        
    def GetValues(self):
        return self.WidthText.Value, self.HeightText.Value

    
dialog=None
def GetFSDialog(parent):
    global dialog
    #Hack in here !: force re-creation of the stuff 
    dialog=None
    if dialog is None:
        dialog=FitSizeDialog(parent)
    return dialog