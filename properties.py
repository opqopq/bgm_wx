"Helpers for property grid back and forth"
import wx.propgrid as wxpg
import wx
import  wx.lib.filebrowsebutton as filebrowse
import wx.lib.scrolledpanel as scrolled
from collections import OrderedDict
import config
        
##Helper for propgrid issue
def Refresh(self):
    self.RefreshGrid()
wxpg.PropertyGridPage.Refresh=Refresh

class MyEnumProperty(wxpg.PyEnumProperty):
    def __init__(self, label, name=wxpg.LABEL_AS_NAME, value=''):
        #print label, name, value
        ###default,thelist=value
        default = value
        thelist=[]
        if default is None:
            default=""
        wxpg.PyEnumProperty.__init__(self, label, name, default)
        if thelist:
            self.SetPyChoices(thelist)

    def GetEditor(self):
        # Set editor to have button
        return "Choice"
    
class SliderPropertyEditor(wxpg.PyEditor):
    def __init__(self):
        wxpg.PyEditor.__init__(self)

    def CreateControls(self, propgrid, property, pos, sz):
        """ Create the actual wxPython controls here for editing the
            property value.You must use propgrid.GetPanel() as parent for created controls.
            Return value is either single editor control or tuple of two
            editor controls, of which first is the primary one and second
            is usually a button.
        """
        try:
            x, y = pos
            w, h = sz
            #h = 64 + 6

            # Make room for button
            textWidth=20
            #bw = propgrid.GetRowHeight()
            #w -= bw

            s = property.GetDisplayedString()


            self.tc = wx.TextCtrl(propgrid.GetPanel(), wxpg.PG_SUBID1, s,(x,y), (textWidth,h),wx.TE_PROCESS_ENTER)
            self.btn = wx.Slider(propgrid.GetPanel(), wxpg.PG_SUBID2, property.GetValue(),0,100,(x+textWidth, y),(w-textWidth, h-y), wx.SL_HORIZONTAL  )
            self.btn.SetBackgroundColour(wx.NamedColour('WHITE'))
            self.btn.Bind(wx.EVT_SLIDER,self.OnSliderUpdate)
            self.tc.Bind(wx.EVT_TEXT,self.OnTextUpdate)
            return (self.tc, self.btn)
        except:
            import traceback
            print(traceback.print_exc())

    def OnTextUpdate(self,evt):
        self.btn.SetValue(int(self.tc.Value))
        
    def OnSliderUpdate(self,evt):
        self.tc.SetValue(str(self.btn.Value))
        
    def UpdateControl(self, property, ctrl):
        "Ctrl is the text control"
        ctrl.SetValue(property.GetDisplayedString())

    def DrawValue(self, dc, rect, property, text):
        if not property.IsValueUnspecified():
            dc.DrawText(property.GetDisplayedString(), rect.x+5, rect.y)

    def OnEvent(self, propgrid, property, ctrl, event):
        """ Return True if modified editor value should be committed to
            the property. To just mark the property value modified, call
            propgrid.EditorsValueWasModified().
        """
        if not ctrl:
            return False

        evtType = event.GetEventType()
        if evtType in( wx.wxEVT_COMMAND_TEXT_ENTER , wx.wxEVT_COMMAND_SLIDER_UPDATED):
            if propgrid.IsEditorsValueModified():
                return True
        
        elif evtType == wx.wxEVT_COMMAND_TEXT_UPDATED:
            #
            # Pass this event outside wxPropertyGrid so that,
            # if necessary, program can tell when user is editing
            # a textctrl.
            event.Skip()
            event.SetId(propgrid.GetId())
            propgrid.EditorsValueWasModified()
            return False

        return False

    def GetValueFromControl(self, property, ctrl):
        """ Return tuple (wasSuccess, newValue), where wasSuccess is True if
            different value was acquired succesfully.
        """

        tc = ctrl
        textVal = tc.GetValue()

        if property.UsesAutoUnspecified() and not textVal:
            return (True, None)

        res, value = property.StringToValue(textVal,
                                            wxpg.PG_EDITABLE_VALUE)

        # Changing unspecified always causes event (returning
        # True here should be enough to trigger it).
        if not res and value is None:
            res = True

        return (res, value)

    def SetValueToUnspecified(self, property, ctrl):
        ctrl.Remove(0,len(ctrl.GetValue()))

    def SetControlStringValue(self, property, ctrl, text):
        ctrl.SetValue(text)

    def OnFocus(self, property, ctrl):
        "ctrl is the text control"
        ctrl.SetSelection(-1,-1)
        ctrl.SetFocus()

class ImgListDialogAdapter(wxpg.PyEditorDialogAdapter):
    """ This demonstrates use of wxpg.PyEditorDialogAdapter.
    """
    def __init__(self):
        wxpg.PyEditorDialogAdapter.__init__(self)

    def DoShowDialog(self, propGrid, property):
        #First find if there is a default path for lloking for images
        frame=propGrid.Parent.Parent
        src_dir=frame.dir
        
        if hasattr(frame,"file"):
            import os.path
            path=os.path.split(frame.file)[0]
        else:
            path="."
        old_value=property.GetValue()
        if not old_value:
            old_value=OrderedDict()
        choices=propGrid.GetValues()['choices']
        dialog=wx.Dialog(frame,size=(500,200),style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        dialog.Title='Image Choice Chooser'
        sizer = wx.BoxSizer(wx.VERTICAL)

        panel = scrolled.ScrolledPanel(dialog, size=(300, 150), style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER)
        fgs1 = wx.FlexGridSizer(cols=2, vgap=4, hgap=4)

        label = wx.StaticText(dialog, -1, "Image for Choices listed in Choices field")
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(panel,1,wx.ALL|wx.EXPAND,2)
        
        fbbs=dict()
        import os.path
        if choices:
            for i,choice in enumerate(choices):
                #box = wx.BoxSizer(wx.HORIZONTAL)
                label = wx.StaticText(panel, -1, choice)
                #box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                fgs1.Add(label, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 5)
                text=filebrowse.FileBrowseButton(panel,startDirectory=path)
                #box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
                fgs1.Add(text, 1, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
                #sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
                fbbs[choice]=text
                #Fill fbb with old value
                _v=old_value.get(choice,"")
                if not os.path.isfile(_v) and os.path.isfile(os.path.join(config.card_folder,_v)):
                        text.SetValue(os.path.join(config.card_folder,_v))
                else:
                        text.SetValue(old_value.get(choice,""))
        #Close button
        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(dialog, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(dialog, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 15)        

        panel.SetSizer( fgs1 )
        panel.SetAutoLayout(1)
        panel.SetupScrolling()

        dialog.Sizer=sizer
        sizer.Fit(dialog)

        dialog.CenterOnScreen()
        # this does not return until the dialog is closed.
        val = dialog.ShowModal()
        done=False
        if val == wx.ID_OK:
            res=OrderedDict()
            for fbb in fbbs:
                res[fbb]=fbbs[fbb].GetValue()
                #here: insert some magic to make this relativ path instead of absolut
                if res[fbb].startswith(src_dir):
                    #print 'relpath with template dir in here'
                    res[fbb]=os.path.relpath(res[fbb],start=src_dir)
                #Same stuff with card_folder
                if res[fbb].startswith(config.card_folder):
                    #print 'relpath with card folder in here'
                    res[fbb]=os.path.relpath(res[fbb],start=config.card_folder)
                
                    
            self.SetValue(res)
            done=True
        dialog.Destroy()
        return done
        
class ImgListProperty(wxpg.PyStringProperty):
    def __init__(self, label, name=wxpg.LABEL_AS_NAME, value=''):
        wxpg.PyStringProperty.__init__(self, label, name, value)

    def GetEditor(self):
        # Set editor to have button
        return "TextCtrlAndButton"

    def GetEditorDialog(self):
        # Set what happens on button click
        return ImgListDialogAdapter()

class SymbolListProperty(wxpg.PyStringProperty):
    def __init__(self, label, name=wxpg.LABEL_AS_NAME, value=''):
        wxpg.PyStringProperty.__init__(self, label, name, value)

    def GetEditor(self):
        # Set editor to have button
        return "TextCtrlAndButton"

    def GetEditorDialog(self):
        # Set what happens on button click
        return SymbolListDialogAdapter()

class SymbolListDialogAdapter(wxpg.PyEditorDialogAdapter):
    """ This demonstrates use of wxpg.PyEditorDialogAdapter.
    """
    def __init__(self):
        wxpg.PyEditorDialogAdapter.__init__(self)

    def DoShowDialog(self, propGrid, property):
        #First find if there is a default path for lloking for images
        frame=propGrid.Parent.Parent
        src_dir=frame.dir
        
        if hasattr(frame,"file"):
            import os.path
            path=os.path.split(frame.file)[0]
        else:
            path="."
        choices=property.GetValue()
        if not choices:
            from collections import OrderedDict
            choices=OrderedDict()
        
        dialog=wx.Dialog(frame,size=(500,200),style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        dialog.Title='Symbols  Choice Chooser'
        sizer = wx.BoxSizer(wx.VERTICAL)

        panel = scrolled.ScrolledPanel(dialog, size=(300, 150), style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER)
        fgs1 = wx.FlexGridSizer(cols=3, vgap=4, hgap=4)

        label = wx.StaticText(dialog, -1, "Images for Symbol listed in Text field")
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(panel,1,wx.ALL|wx.EXPAND,2)
        
        self.fbbs=dialog.fbbs=dict()
        import os.path
        for choice,fpath in enumerate(choices.values()):
            #box = wx.BoxSizer(wx.HORIZONTAL)
            cb=wx.CheckBox(panel)
            fgs1.Add(cb,0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 5)
            label = wx.TextCtrl(panel, -1, choice)
            #box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            fgs1.Add(label, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 5)
            text=filebrowse.FileBrowseButton(panel,initialValue=fpath)
            #box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
            fgs1.Add(text, 1, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
            #sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
            self.dialog.fbbs[cb]=text
            cb._fbb=text
            cb._tc=label
            if not os.path.isfile(fpath) and os.path.isfile(os.path.join(config.card_folder,fpath)):
                    text.SetValue(os.path.join(config.card_folder,_v))
        #Add Remove Button
        box=wx.BoxSizer()
        btn=wx.Button(dialog,label="+",size=(30,-1))
        box.Add(btn)
        btn.Bind(wx.EVT_BUTTON,self.OnAddSymbol)
        btn=wx.Button(dialog,label="-",size=(30,-1))
        btn.Bind(wx.EVT_BUTTON,self.OnRemoveSymbol)
        box.Add(btn)
        sizer.Add(box,0,wx.ALL,10)
        #Close button
        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(dialog, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(dialog, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 15)        

        panel.SetSizer( fgs1 )
        panel.SetAutoLayout(1)
        panel.SetupScrolling()
        self.panel=panel
        dialog.Sizer=sizer
        dialog.SetAutoLayout(1)
        
        sizer.Fit(dialog)

        dialog.CenterOnScreen()
        # this does not return until the dialog is closed.
        val = dialog.ShowModal()
        done=False
        if val == wx.ID_OK:
            res=OrderedDict()
            for c in panel.GetChildren():
                if c.__class__ == wx.CheckBox and c.Shown:
                    label=c._tc.Value
                    path=c._fbb.GetValue() or "" 
                    print "path is", type(path), "'%s'"%path , "'%s'"%c._fbb.GetValue()
                    print 'cfold is',type(config.card_folder), "'%s'"%config.card_folder
                    if path.startswith(src_dir):
                        path=os.path.relpath(path,start=src_dir)
                    elif path.startswith(config.card_folder):
                        path=os.path.relpath(path,start=config.card_folder)
                    res[label]=path
            self.SetValue(res)
            done=True
        dialog.Destroy()
        return done
        
    def OnAddSymbol(self,evt):
        cb=wx.CheckBox(self.panel)
        self.panel.Sizer.Add(cb,0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 5)
        label = wx.TextCtrl(self.panel, -1, "[Symbol]")
        #box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.panel.Sizer.Add(label, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 5)
        text=filebrowse.FileBrowseButton(self.panel)
        #box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.panel.Sizer.Add(text, 1, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        #sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.fbbs[cb]=text
        cb._tc=label
        cb._fbb=text
        self.panel.Sizer.Layout()

    def OnRemoveSymbol(self,evt):
        for c in self.panel.GetChildren():
            if c.__class__ == wx.CheckBox:
                if c.Value and c.Shown:
                    del self.fbbs[c]
                    self.panel.Sizer.Remove(c._tc)
                    self.panel.Sizer.Remove(c._fbb)
                    self.panel.Sizer.Remove(c)

                    c._tc.Show(False)
                    c._fbb.Show(False)
                    c.Show(False)
                    self.panel.Sizer.Layout()
        self.panel.Refresh()
                    
            
        
    
class SuperFontDialogAdapter(wxpg.PyEditorDialogAdapter):
    """ This demonstrates use of wxpg.PyEditorDialogAdapter.
    """
    def __init__(self):
        wxpg.PyEditorDialogAdapter.__init__(self)

    def DoShowDialog(self, propGrid, property):
        #First find if there is a default path for lloking for images
        frame=propGrid.Parent.Parent
        data = wx.FontData()
        data.EnableEffects(True)
        data.SetColour(property.GetPropertyByName('color').GetValue())
        font=wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.FaceName=property.GetPropertyByName('name').GetValue()
        font.PointSize=property.GetPropertyByName('size').GetValue()
        font.Weight=getattr(wx,'FONTWEIGHT_'+property.GetPropertyByName('weight').GetValue().upper())
        font.Style=getattr(wx,'FONTSTYLE_'+property.GetPropertyByName('style').GetValue().upper())
        font.Family=getattr(wx,'FONTFAMILY_'+property.GetPropertyByName('Family').GetValue().upper())
        font.Underlined=property.GetPropertyByName('underline').GetValue()
        data.SetInitialFont(font)

        dialog=wx.FontDialog(frame,data)
        dialog.CenterOnScreen()
        # this does not return until the dialog is closed.
        
        val = dialog.ShowModal()
        done=False
        if val == wx.ID_OK:
            data = dialog.GetFontData()
            font = data.GetChosenFont()
            colour = data.GetColour()
            #self.SetValue(font)
            property.GetPropertyByName('color').SetValue(colour)
            property.GetPropertyByName('name').SetValue(font.FaceName)
            property.GetPropertyByName('size').SetValue(font.PointSize)
            property.GetPropertyByName('weight').SetValue(font.WeightString.split('_')[1].lower())
            property.GetPropertyByName('style').SetValue(font.StyleString.split('_')[1].lower())
            property.GetPropertyByName('Family').SetValue(font.FamilyString.split('_')[1].lower())
            property.GetPropertyByName('underline').SetValue(font.Underlined) 
            self.SetValue('%s;%s;%s;%s;%s;%s'%(font.FaceName,font.PointSize,font.WeightString,font.StyleString,str(font.Underlined).lower(),str(colour)))
            done=True
        dialog.Destroy()
        return done
    
class SuperFontProperty(wxpg.PyStringProperty):
    def __init__(self, label, name=wxpg.LABEL_AS_NAME, value=''):
        wxpg.PyStringProperty.__init__(self, label, name, value)
        from widgets import FontTemplate
        for item in FontTemplate.specific_params:
            name, thelist=item
            _t,_v=thelist
            p=self.AppendChild(forms[_t](name))
            p.SetValue(_v)
        #Now fill default property
        font=wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.GetPropertyByName('name').SetValue(font.FaceName)
        self.GetPropertyByName('size').SetValue(font.PointSize)
        self.GetPropertyByName('weight').SetValue(font.WeightString.split('_')[1].lower())
        self.GetPropertyByName('style').SetValue(font.StyleString.split('_')[1].lower())
        self.GetPropertyByName('underline').SetValue(font.Underlined)
        self.GetPropertyByName('color').SetValue(wx.Colour())
        self.GetPropertyByName('Family').SetValue(font.FamilyString.split('_')[1].lower())
        #self.GetPropertyByName('scale down to').SetValue(font.PointSize)
        self.SetValue('%s;%s;%s;%s;%s;%s'%(font.FaceName,font.PointSize,font.WeightString,font.StyleString,str(font.Underlined).lower(),str(wx.Colour())))

    def GetEditor(self):
        # Set editor to have button
        return "TextCtrlAndButton"

    def GetEditorDialog(self):
        # Set what happens on button click
        return SuperFontDialogAdapter()

def strbool(x):
    if x.lower()=='false':
        return False
    return bool(x)

def strcolor(x):
    if type(x)==type(wx.Colour()):
        return x
    if wx.NamedColour(x).IsOk():
        return wx.NamedColour(x)
    if not x:
        return wx.Colour()
    if x=="None":
        return wx.Colour()
    exec 'c=wx.Colour%s'%x
    return c
    
iso=lambda x:x

#map type of an object and its property type
forms={
    "str":wxpg.LongStringProperty,
    "int":wxpg.IntProperty,
    "float":wxpg.FloatProperty,
    "slider":wxpg.IntProperty,
    "bool":wxpg.BoolProperty,
    "dir":wxpg.DirProperty,
    "file":wxpg.FileProperty,
    "date":wxpg.DateProperty,
    "font":wxpg.FontProperty,
    "font":SuperFontProperty,
    "color":wxpg.ColourProperty,
    "img":wxpg.ImageFileProperty, 
    'list':wxpg.ArrayStringProperty,
    'imglist':ImgListProperty,
    'mchoices':wxpg.MultiChoiceProperty,
    'choice':wxpg.EnumProperty,
    'new_choice':MyEnumProperty,
    'symbols':SymbolListProperty,

}
#convert text to real value
xfos={
    "str":lambda x:unicode(x,'cp1252'),
    "int":int,
    "float":float,
    "bool":strbool,
    'color':strcolor,  
}

#properties to add to propertygrid

properties={
    "bool":(("UseCheckbox", True),),
    "file":((wxpg.PG_FILE_SHOW_FULL_PATH, 0),(wxpg.PG_FILE_INITIAL_PATH,config.deckdir)),
    "date":((wxpg.PG_DATE_PICKER_STYLE, wx.DP_DROPDOWN|wx.DP_SHOWCENTURY)),      
}
#editors to add to propertygrid
editors={
    "int":"SpinCtrl",
    "slider":"SliderPropertyEditor",

}
##Matching between Elt Type and propertyGrid type:
typematch={
    'Text':'str',
    'StaticImage':'img',
    'Image':'img',
    'Info':'str',
#    'Set':'str',
    'Choice':'choice',
    'MChoice':'mchoices',
    'Color':'color',
}