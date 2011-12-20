import wx
import wx.propgrid as wxpg
import wx.lib.agw.buttonpanel as bp

import os.path,os

if __name__=='__main__':
    app=wx.PySimpleApp()

from widgets import ElementsClass,FieldFromValues

todos=[
    "Create symbol transfo for text",
    "Enhance object view, to translate: default img, font, rotation, bk color (if exts)"
    "add some opacity value, like the mask one"
]

todosmese=[
    'add Set Loader',
    'add template loader',
]
for todo in todos:
    print "[Designer]:",todo

MSE=False
    
##Helper for pickle
 # Create a new reduce function:
def _reduce_Font(self):
    if not self.IsOk():
         # invalid font, need a valid font to pickle
         return (self.__class__, (-1, -1, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    else:
        return (self.__class__,
        (self.GetPointSize(),
            self.GetFamily(),
            self.GetStyle(),
            self.GetWeight(),
            self.GetUnderlined(),
            self.GetFaceName(),
            self.GetDefaultEncoding())
        )
# Replace the original Font.__reduce__ method:
wx.Font.__reduce__ = _reduce_Font

def _reduce_Color(self):
    if not self.IsOk():
        return wx.Colour()
    else:
        return (self.__class__,(self.Red(),self.Green(),self.Blue(),self.Alpha()))
wx.Colour.__reduce__= _reduce_Color

if __name__=='__main__':
    MSE=True
    for todo in todosmese:
        print "[Designere][MSE]:",todo

class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, parent):
        wx.FileDropTarget.__init__(self)
        self.parent = parent

    def OnDropFiles(self, x, y, files):
        for f in files:
            if f.endswith('.tmpl') :
                self.parent.LoadTemplate(f)
                return

class WYSIFrame(wx.Frame):
    def __init__(self,mainframe,target=None,startOldFile=False):
        wx.Frame.__init__(self, mainframe, -1, "New Template.tmpl*", style=wx.DEFAULT_FRAME_STYLE | wx.TINY_CAPTION_HORIZ)
        self.Size=wx.Size(900,600)
        self.changed=False
        self.saved=False
        self.file=''
        self.dir='.'
        self.pycrust=None
        #Save the treectrlitem we have to change once the windows is closed or the template is save
        self.TemplateTreeItem=target
        if mainframe:
            self.dir=mainframe.deckdir
        self.statusbar=wx.StatusBar(self)
        self.SetStatusBar(self.statusbar)
        #Create Tree
        self.tree=wx.TreeCtrl(self,-1,size=(250,100),style=wx.TR_LINES_AT_ROOT|wx.TR_DEFAULT_STYLE|wx.TR_HAS_BUTTONS)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED,self.OnTreeSelectionChanged)
        self.propgrid= wxpg.PropertyGridManager(self, style= wxpg.PG_SPLITTER_AUTO_CENTER |wxpg.PG_EX_HELP_AS_TOOLTIPS| wxpg.PG_TOOLBAR)
        self.propgrid.Bind( wxpg.EVT_PG_CHANGED, self.OnPropGridChange)
        #from deckmvc import MSEGrid
        #self.deckgrid=MSEGrid(self)
        self.CreateImageList()
        self.tree.SetImageList(self.il)
        self.CreateToolbar()
        from oglwin import TW
        self._thewin=TW(self)        
        #keep the elts details
        self.CreateTree()
        self.CreateBlankTemplate()
        #Evt management
        #####self.Bind(wx.EVT_CHAR_HOOK,  self.OnKeyDown)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        #Sizing
        self._init_aui()
        #dND
        self.SetDropTarget(MyFileDropTarget(self))
        #Open Last opened file
        if startOldFile:
            import os.path
            if os.path.isfile('designer_last_file'):
                dst=file('designer_last_file','rb').read()
                if os.path.isfile(dst):
                    self.LoadTemplate(dst)

    def CreateImageList(self):
        isz = (16,16)
        isz = (32,32)
        isz = tsize=(48,48)
        il = wx.ImageList(isz[0], isz[1])
        #il.fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        #il.fldropenidx = il.Add(wx.Bitmap('img/Actions-window-plus-icon.png').ConvertToImage().Rescale(*isz).ConvertToBitmap())
        il.fileidx     = il.Add(wx.Bitmap('img/view_tree.png').ConvertToImage().Rescale(*isz).ConvertToBitmap())
        #il.scriptidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_EXECUTABLE_FILE, wx.ART_OTHER ,isz))
        #il.templidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_LIST_VIEW, wx.ART_OTHER ,isz))        
        il.textelt     = il.Add(wx.Bitmap('img/font.png').ConvertToImage().Rescale(*isz).ConvertToBitmap())        
        il.imgelt     = il.Add(wx.Bitmap('img/image.png').ConvertToImage().Rescale(*isz).ConvertToBitmap())        
        il.choiceelt   = il.Add(wx.Bitmap('img/kmenuedit.png').ConvertToImage().Rescale(*isz).ConvertToBitmap())   
        il.infoelt      = il.Add(wx.Bitmap('img/info.png').ConvertToImage().Rescale(*isz).ConvertToBitmap())        
        il.setelt       = il.Add(wx.Bitmap('img/misc.png').ConvertToImage().Rescale(*isz).ConvertToBitmap())        
        #il.excel_bmp=il.Add(wx.Bitmap('excel_icon.jpg').ConvertToImage().Rescale(*isz).ConvertToBitmap())
        il.setmaker_bmp=il.Add(wx.Bitmap('img/make_kdevelop.png').ConvertToImage().Rescale(*isz).ConvertToBitmap())
        il.staticelt=il.Add(wx.Bitmap('img/indeximg.png').ConvertToImage().Rescale(*isz).ConvertToBitmap())
        il.new_bmp =  il.Add(wx.Bitmap('img/filenew.png').ConvertToImage().Rescale(*tsize).ConvertToBitmap())
        il.open_bmp = il.Add(wx.Bitmap('img/fileopen.png').ConvertToImage().Rescale(*isz).ConvertToBitmap())
        il.save_bmp = il.Add(wx.Bitmap('img/filesave.png').ConvertToImage().Rescale(*tsize).ConvertToBitmap())
        il.saveas_bmp = il.Add(wx.Bitmap('img/filesaveas.png').ConvertToImage().Rescale(*tsize).ConvertToBitmap())
        #text_bmp = wx.ArtProvider.GetBitmap(wx.ART_HELP_SETTINGS, wx.ART_TOOLBAR, tsize)
        #img_bmp= wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_TOOLBAR, tsize)
        il.mse_bmp= il.Add(wx.Bitmap('img/install.png').ConvertToImage().Rescale(*tsize).ConvertToBitmap())
        il.del_bmp= il.Add(wx.Bitmap('img/editdelete.png').ConvertToImage().Rescale(*tsize).ConvertToBitmap())
        il.import_bmp= il.Add(wx.Bitmap('img/import.png').ConvertToImage().Rescale(*tsize).ConvertToBitmap())
        il.install_bmp= il.Add(wx.Bitmap('img/ico_surveys.gif').ConvertToImage().Rescale(*tsize).ConvertToBitmap())
        il.genimg_bmp= il.Add(wx.Bitmap('img/image-icon.png').ConvertToImage().Rescale(*tsize).ConvertToBitmap())
        il.colorelt= il.Add(wx.Bitmap('img/color_box.png').ConvertToImage().Rescale(*tsize).ConvertToBitmap())
        il.debugelt= il.Add(wx.Bitmap('img/debug.png').ConvertToImage().Rescale(*tsize).ConvertToBitmap())
        il.keywordelt=il.Add(wx.Bitmap('img/keyword.png').ConvertToImage().Rescale(*tsize).ConvertToBitmap())
        il.mseelt=il.Add(wx.Bitmap('img/mse.jpg').ConvertToImage().Rescale(*tsize).ConvertToBitmap())        
        il.symbolelt=il.Add(wx.Bitmap('img/symbol_icon.png').ConvertToImage().Rescale(*tsize).ConvertToBitmap())        
        self.il=il

    def CreateFieldsPanel(self):
        import sys
        from wx.lib.agw import ultimatelistctrl as ULC
        # create the list control
        l= ULC.UltimateListCtrl(self, -1,size=(200,400),agwStyle=wx.LC_ICON | wx.LC_AUTOARRANGE )#|ULC.ULC_HEADER_IN_ALL_VIEWS)

        # assign the image list to it
        l.AssignImageList(self.il, wx.IMAGE_LIST_NORMAL)
        l.AssignImageList(self.il, 0)

        #~ info = ULC.UltimateListItem()
        #~ info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_FORMAT
        #~ info._format = wx.LIST_FORMAT_CENTER
        #~ info._text = "Type"        
        #~ l.InsertColumnInfo(0, info)

        index = l.InsertImageStringItem(0, "Symbols",self.il.symbolelt)
        index = l.InsertImageStringItem(0, "Info",self.il.infoelt)
        index = l.InsertImageStringItem(0, "Set",self.il.setelt)
        index = l.InsertImageStringItem(0, "Color",self.il.colorelt)
        #index = l.InsertImageStringItem(0, "MChoice",self.il.choiceelt)
        index = l.InsertImageStringItem(0, "Choice",self.il.choiceelt)
        index = l.InsertImageStringItem(0, "Image",self.il.imgelt)
        #index = l.InsertImageStringItem(0, "StaticImage",self.il.imgelt)
        index = l.InsertImageStringItem(0, "Text",self.il.textelt)
        l.Bind(ULC.EVT_LIST_ITEM_ACTIVATED,self.OnAddItem)
        
        return l
        
    def CreatePackagePanel(self):
        from wx.lib.agw import ultimatelistctrl as ULC
        # create the list control
        l= ULC.UltimateListCtrl(self, -1,agwStyle=wx.LC_ICON | wx.LC_AUTOARRANGE )
        # assign the image list to it
        l.AssignImageList(self.il, wx.IMAGE_LIST_NORMAL)
        icons=[self.il.setmaker_bmp,self.il.install_bmp, self.il.genimg_bmp,self.il.mse_bmp,self.il.import_bmp]

        names=[
                #"Localisation & Help Files",
                #"Export Template",
                #"Include bundles"
                ##"Template Exporter",
                "Set Maker",
                ##"Installer Maker",
                "Install Template",
                "Images Maker",
                "Export Template",
                'Import Template',
                ]
        
        for i,name in enumerate(zip(names,icons)):
            index = l.InsertImageStringItem(i, *name)
        l.Bind(ULC.EVT_LIST_ITEM_ACTIVATED,self.OnHelpersActivated)
        
        #for i,name in enumerate(names):
        #    index = l.InsertImageStringItem(i, name,self.il.textelt)
        return l

    def CreateHelpersPanel(self):        
        from wx.lib.agw import ultimatelistctrl as ULC
        # create the list control
        l= ULC.UltimateListCtrl(self, -1,agwStyle=wx.LC_ICON | wx.LC_AUTOARRANGE )
        # assign the image list to it
        l.AssignImageList(self.il, wx.IMAGE_LIST_NORMAL)
        icons=[self.il.staticelt,self.il.install_bmp]

        names=[
                "StaticImage",
                "Choice Maker"
                ]
        for i,name in enumerate(zip(names,icons)):
            index = l.InsertImageStringItem(i, *name)
        l.Bind(ULC.EVT_LIST_ITEM_ACTIVATED,self.OnHelpersActivated)
        return l
        
    def InstallTemplate(self,evt):
        #Create Template and put it in MSE Path
        import os.path
        self.OnMSEExport(evt,startfile=False)
        path=self.dir
        tmp=self.elts[0]
        name=tmp.GetValues()['short name']
        sname=tmp.GetValues()['style short name']
        pg=os.path.join(path,'%s.mse-game'%name)
        ps=os.path.join(path,'%s-%s.mse-style'%(name,sname))
        #now copy it on mse path
        from config import MSE_PATH
        mse_path=os.path.split(MSE_PATH)[0]
        if not os.path.isdir(mse_path):
            print "mse path not good:'%s'"%mse_path
            return
        from shutil import move, copy, Error
        from glob import glob
        try:
            move(pg,os.path.join(mse_path,'data'))
        except Error,e:
            dst=os.path.join(mse_path,'data')
            for fname in glob(os.path.join(pg,'*')):
                try:
                    copy(fname,os.path.join(dst,'%s.mse-game'%name))
                except IOError,e:
                    pass
        try:
            move(ps,os.path.join(mse_path,'data'))
        except Error,e:
            dst= os.path.join(mse_path,'data')
            for fname in glob(os.path.join(ps,'*')):
                try:
                    copy(fname, os.path.join(dst,'%s-%s.mse-style'%(name,sname)))
                except IOError,e:
                    pass
        self.statusbar.SetStatusText('Template installed')
        
    def OnHelpersActivated(self,evt):
        action=evt.GetText()
        if action=="Set Maker":
            #Generate MSE Set from set in template
            self.OnGenSet()
        elif action=="StaticImage":
            #Add a static image to help design template
            self.OnAddItem(evt)
        elif action=="Install Template":
            self.InstallTemplate(evt)
        elif action=="Choice Maker":
            #Ask for a list of image. Create the choice elt based on that
            #First, get the images list
            imglist=[]
            dlg = wx.FileDialog(self, message="Choose Images for Choice",defaultDir=self.dir, defaultFile="",wildcard="All files (*.*)|*.*",style=wx.OPEN | wx.MULTIPLE)
            # Show the dialog and retrieve the user response. If it is the OK response, 
            # process the data.
            if dlg.ShowModal() == wx.ID_OK:
                # This returns a Python list of files that were selected.
                imglist = dlg.GetPaths()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return
            Type="choice"
            self.changed=True
            if not self.Title[-1]=='*':
                self.Title+='*'
            name='%s%d'%(Type,self.tree.GetChildrenCount(self.tree.RootItem)+1)
            blank=ElementsClass[Type]()
            blank.name=name
            item=self.AddElt(blank)
            _elt,_shape,_page=self.tree.GetPyData(item)
            #Change choices & choices image info
            choices=[]
            from collections import OrderedDict
            import os.path
            choicesimg=OrderedDict()
            for x in imglist:
                k=os.path.splitext(os.path.split(x)[-1])[0]
                choices.append(k)
                choicesimg[k]=x
                if x.startswith(self.dir):
                    choicesimg[x]=os.path.relpath(x,start=self.dir)
            _page.GetPropertyByName('choices').SetValue(choices)
            _page.GetPropertyByName('choice images').SetValue(choicesimg)
        elif action=='Export Template':
            self.OnMSEExport(evt)
        elif action=='Import Template':
            self.OnImportGame(evt)
        elif action=="Images Maker":
            #First ensure current template is installed
            self.InstallTemplate(evt)
            #Generate Set then create image for sets & remove set
            import os
            dlg = wx.DirDialog(self, "Choose a destination directory:", style=wx.DD_DEFAULT_STYLE, defaultPath=self.dir)
            if dlg.ShowModal() == wx.ID_OK:
                path=dlg.GetPath()
                #self.dir=path
                # Only destroy a dialog after you're done with it.
                dlg.Destroy()
            else:
                return
            #clock
            try:
                wx.BeginBusyCursor()
                sets=self.GenerateSetFiles('tmp')#force dst dir for mse.set file to tmp
                #then create image
                import MSE
                for setname in sets:
                    MSE.GenerateImages(setname,path)
                    #Now remove set file
                    os.remove(setname)
            #unclcok
            finally:
                wx.EndBusyCursor()
            import os
            os.startfile(path)
            
    def OnAddItem(self,evt):
        Type=evt.GetText()
        self.changed=True
        if not self.Title[-1]=='*':
            self.Title+='*'
        name='%s%d'%(Type,self.tree.GetChildrenCount(self.tree.RootItem)+1)       
        klass=ElementsClass.get(Type.lower())
        if klass is None:
            raise ValueError('Unknown Type:%s'%Type)
        blank=klass()        
        blank.name=name
        self.AddElt(blank)

    def CreateShapeToolbar(self):
        import wx.lib.agw.aui as aui
        ID_SampleItem=666
        # create some toolbars
        tb1 = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                             agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tb1.SetToolBitmapSize(wx.Size(16, 16))
        tb1.AddSimpleTool(ID_SampleItem+1, "Duplicate", wx.Bitmap('img/duplicate.png'),'duplicate')
        tb1.Bind(wx.EVT_MENU,self.OnDuplicate,id=ID_SampleItem+1)
        tb1.AddSimpleTool(ID_SampleItem+2, "Delete", wx.Bitmap('img/delete.png'),'remove')
        tb1.Bind(wx.EVT_MENU,self.OnDelElt,id=ID_SampleItem+2)
        tb1.AddSimpleTool(ID_SampleItem+3, "Center H", wx.Bitmap('img/btn_center_horizontal.png'),'center H')
        tb1.Bind(wx.EVT_MENU,self.OnCenterHElt,id=ID_SampleItem+3)
        tb1.AddSimpleTool(ID_SampleItem+4, "Center V", wx.Bitmap('img/btn_center_vertical.png'),'center V')
        tb1.Bind(wx.EVT_MENU,self.OnCenterVElt,id=ID_SampleItem+4)
        tb1.AddSimpleTool(ID_SampleItem+5, "Max H", wx.Bitmap('img/max_h.gif'),'max H')
        tb1.Bind(wx.EVT_MENU,self.OnMaxHElt,id=ID_SampleItem+5)
        tb1.AddSimpleTool(ID_SampleItem+6, "Max V", wx.Bitmap('img/max_v.gif'),'max V')
        tb1.Bind(wx.EVT_MENU,self.OnMaxVElt,id=ID_SampleItem+6)
        tb1.Realize()
        return tb1
    
    def _init_aui(self):
        import wx.lib.agw.aui as aui
        self._mgr=aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        #self._mgr.AddPane(self.deckgrid, aui.AuiPaneInfo().Name("deckgrid").Caption("DeckGrid").Bottom().CloseButton(False).MaximizeButton(True))
        self._mgr.AddPane(self.titleBar, aui.AuiPaneInfo().Name("toolbar").Top().CloseButton(False).MaximizeButton(False).GripperTop(False).Floatable(False).CaptionVisible(False))
        self._mgr.AddPane(self.tree, aui.AuiPaneInfo().Name("Elements").Caption("Elements").Right().CloseButton(False).MaximizeButton(True))
        self._mgr.AddPane(self.CreateShapeToolbar(), aui.AuiPaneInfo().Name("ShapeTb").Caption("Element Functions").Right().CloseButton(False).MaximizeButton(False).Fixed())
        self._mgr.AddPane(self.propgrid, aui.AuiPaneInfo().Name("Options").Caption("Options").Right().CloseButton(False).MaximizeButton(True))
        #Left FPB
        self._mgr.AddPane(self.CreateFieldsPanel(), aui.AuiPaneInfo().Name("fields").Caption("Fields").Left().MinimizeButton(True).CloseButton(False).MinimizeMode(aui.AUI_MINIMIZE_CAPT_SMART))
        self._mgr.AddPane(self.CreatePackagePanel(), aui.AuiPaneInfo().Name("mse").Caption("MSE").Left().MinimizeButton(True).CloseButton(False).MinimizeMode(aui.AUI_MINIMIZE_CAPT_SMART))#,target=self._mgr.GetPane("fields"))
        self._mgr.AddPane(self.CreateHelpersPanel(), aui.AuiPaneInfo().Name("helpers").Caption("Helpers").Left().MinimizeButton(True).CloseButton(False).MinimizeMode(aui.AUI_MINIMIZE_CAPT_SMART))#,target=self._mgr.GetPane("fields"))
        self._mgr.AddPane(self._thewin, aui.AuiPaneInfo().Name("template").Caption("Template").Center().CloseButton(False).MaximizeButton(True))
        self._mgr.Update()
        
    def OnKeyDown(self,evt):
        code=evt.GetKeyCode()
        if code==wx.WXK_DELETE:
            self.OnDelElt(evt)
            return
        elif code in (ord('d') , ord('D')):#duplicate current element
            if evt.ControlDown():
                self.OnDuplicate(evt)
            
        elif code in (wx.WXK_LEFT,wx.WXK_RIGHT,wx.WXK_UP,wx.WXK_DOWN):
            step=1
            if code in (wx.WXK_LEFT,wx.WXK_UP):
                step=-1
            if evt.ControlDown():
                step*=20
            name='left'
            if code in (wx.WXK_UP,wx.WXK_DOWN):
                name='top'
            #Get Current Page
            item=self.tree.Selection
            res=self.tree.GetPyData(item)
            if res is None:
                return
            elt,shape,page=res
            prop=page.GetPropertyByName(name)
            prop.SetValue(prop.GetValue()+step)
            self.OnPropGridChange(evt)
            return
        #~ elif code ==wx.WXK_F4:
            #~ if evt.AltDown():
                #~ self.Close()
        #evt keep on going
        evt.Skip()
        
    def OnPropGridChange(self,evt):
        self.changed=True
        item=self.tree.Selection
        if item is None or item is self.tree.RootItem:
            return
        res=self.tree.GetPyData(item)
        if res is None:
            return
        elt,shape,page=res
        ## Specific changes for non gui element (set & else...)
        if elt.Type in ('Set',):
            return
        ##Basic Properties Changes
        names=['height','width']
        if elt.Type=='template':
            names=['card height','card width']
        funcs=[shape.SetHeight,shape.SetWidth]
        for n,f in zip(names,funcs):
            p=page.GetPropertyByName(n)
            _v=p.GetValue()
            f(_v)
            elt[n]=_v
        if elt.Type in ('staticimage','image'):
            #resize bitmap
            import os.path
            if elt['default'] and os.path.isfile(elt['default']):
                bmp=wx.Bitmap(elt['default'])
                bmp=bmp.ConvertToImage().Rescale(elt['width'],elt['height']).ConvertToBitmap()
                if elt['mask'] and os.path.isfile(elt['mask']):
                    mask=wx.Bitmap(elt['mask'])
                    bmp.SetMask(wx.Mask(mask))
                if hasattr(shape,'SetBitmap'):
                    shape.SetBitmap(bmp)
        if elt.Type=='template':
            _vx=_vy=0
        else:
            _vx=page.GetPropertyByName('top').GetValue()
            _vy=page.GetPropertyByName('left').GetValue()
        shape.SetY(_vx+shape.GetHeight()/2)
        shape.SetX(_vy+shape.GetWidth()/2)
        elt['top']=_vx
        elt['left']=_vy
        #Name Change
        if elt.Type=="template":
            new_name=p=page.GetPropertyByName('short name').GetValue()
        else:
            new_name=p=page.GetPropertyByName('name').GetValue()
        if elt.name!=new_name:
            old_name=elt.name
            elt.name=elt['name']=new_name
            shape.text=elt.name
            shape.ClearText()
            for line in new_name.split('\n'):shape.AddText(line)
            self.tree.SetItemText(shape._treeitem,new_name)
            #Toolbar change - it is the first children of the prop grid manager
            ptb=self.propgrid.Children[1]
            for i in range(ptb.ToolsCount):
                if ptb.GetToolByPos(i).Label==old_name:
                    ptb.GetToolByPos(i).Label=new_name
                    ptb.GetToolByPos(i).ShortHelp=new_name
                    ptb.Refresh()
            #page.Set
        ##Specific property changes
        if elt.Type in ('staticimage','image'):
            import os.path
            newdefault=page.GetPropertyByName('default').GetValue()
            if newdefault!=elt['default']:
                elt['default']=newdefault
                if elt['default'] and os.path.isfile(elt['default']):
                    filename=newdefault
                    bmp=wx.Bitmap(filename)
                    bmp=bmp.ConvertToImage().Rescale(elt['width'],elt['height']).ConvertToBitmap()
                    if elt['mask'] and os.path.isfile(elt['mask']):
                        mask=wx.Bitmap(elt['mask'])
                        bmp.SetMask(wx.Mask(mask))
                    if hasattr(shape,'SetBitmap'):shape.SetBitmap(bmp)
                    
        self._thewin.Refresh()
        
    def OnTreeSelectionChanged(self,evt):
        #Select the corresponding propgrid page
        item=self.tree.Selection
        if item is None:
            return
        if item is self.tree.RootItem:
            self.propgrid.SelectPage(0)
            return
        res=self.tree.GetPyData(item)
        if res is None:
            return
        elt,shape,page=res
        self.propgrid.SelectPage(page)
    
    def CreatePropGridPage(self,Element):
        from MSE import ENUMS
        from properties import forms,editors,properties
        page= self.propgrid.AddPage( Element.name)
        labels=("Game","Style")
        element=ElementsClass[Element.Type]()
        for Label in labels:
            page.Append(wxpg.PropertyCategory('MSE %s Properties'%Label))
            for pName in element.params:
                p=element.params[pName]
                if p.component!=Label.lower():
                    continue
                _p=forms[p.typ]
                prop=page.Append(_p(pName))
                #SPecial case
                _data=editors.get(p.typ,None)
                if _data:
                    page.SetPropertyEditor(pName,_data)
                #Special hack for enums
                if _p in (wxpg.MultiChoiceProperty,wxpg.EnumProperty):
                    prop.SetPyChoices(ENUMS[pName])
                _data=properties.get(p.typ,())
                if _data:
                    for pgprop in _data:                   
                        page.SetPropertyAttribute(pName, *pgprop)
                prop.SetValue(p.value)
        page.Type=Element.Type
        return page

    def CreateTree(self,name="Template"):        
        self.elts=list()
        self.tree.DeleteAllItems()
        self.tree.AddRoot(name,image=self.il.fileidx)
        self.tree.Expand(self.tree.RootItem)
        #Create propgrid also
        for i in reversed(range(self.propgrid.GetPageCount())): 
            self.propgrid.RemovePage(i)
        #Remove all existing shape also
        for shape in self._thewin.shapes:
            shape.Delete()
        self._thewin.shapes=[]
    
    def CreateBlankTemplate(self):
        if self.Parent:
            print_size=self.Parent.fitting_size
        else:
            from config import print_size
        import widgets
        tmp=widgets.GameTemplate()
        tmp.params['card height'].value=print_size[1]
        tmp.params['card width'].value=print_size[0]
        tmp.name='Template'
        self.AddElt(tmp)
        
    def CreateToolbar(self):
        self.titleBar = bp.ButtonPanel(self, -1, "Template Designer",agwStyle=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)
        #
        self.titleBar.SetInitialSize(wx.Size(2000,66))
        self.titleBar.Size=wx.Size(66,-1)
        #Game ID Field
        bmps=[self.il.new_bmp,self.il.open_bmp,self.il.save_bmp,self.il.saveas_bmp,self.il.debugelt,self.il.mseelt]
        shs=["New","Open","Save","Save as","Debug",'MSE']
        lhs=["Reset Current Template","Open template file","Save Current Template","Save current template As",'Start debug shell','Start MSE']
        cbs=[self.OnNew,self.OnOpen,self.OnSave,self.OnSaveAs,self.OnPyShell,self.OnStartMSE]
        
        for bmp,shortHelp,longHelp,cb in zip(bmps,shs,lhs,cbs):        
            btn = bp.ButtonInfo(self.titleBar, wx.NewId(),self.il.GetBitmap(bmp),shortHelp=shortHelp, longHelp=longHelp)
            self.titleBar.AddButton(btn)
            self.Bind(wx.EVT_BUTTON, cb,id=btn.GetId())

        self.titleBar.DoLayout()

    def OnImportGame(self,evt):
        #Reset dispplay
        self.changed=False
        self.saved=False
        self.elts=list()
        self.CreateTree()
        from config import MSE_PATH
        import os.path
        import MSE
        if not os.path.isfile(MSE_PATH):
            dlg = wx.FileDialog(self, "Where is MSE ?", self.dir, "", "All Files(*.*)|*.*", wx.OPEN)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    # Your code
                    filename=dlg.GetPath()
                    import config
                    config.MSE_PATH=MSE_PATH=filename
                    config.set('mse','path',MSE_PATH)
            finally:
                dlg.Destroy()
        thedir,mse=os.path.split(MSE_PATH)
        src=os.path.join(thedir,'data')
        games=set()
        styles=dict()
        others=dict()
        names=[x for x in os.listdir(src) if os.path.isdir(os.path.join(src,x)) and len(x.split('.'))>1]
        for name in names:
            game_name,_typ=name.split('.',1)
            if _typ.lower()=="mse-game":
                games.add(game_name)
            elif _typ.lower()=='mse-style':
                gname,style_name=game_name.split('-',1)
                styles.setdefault(gname,[]).append(style_name)
            else:
                others.setdefault(_typ,[]).append(game_name)
        #Now create a frame with  all games & their style
        f=wx.Frame(self)
        f.Title="MSE Template Browser"
        f.Sizer=wx.BoxSizer()
        tree=wx.TreeCtrl(f)
        root=tree.AddRoot('MSE Templates:')
        for g in sorted(games):
            item=tree.AppendItem(root,g)
            tree.SetPyData(item,('game',g))
            if g in styles:
                for style in sorted(styles[g]):
                    sitem=tree.AppendItem(item,style)
                    tree.SetPyData(sitem,('style','%s-%s'%(g,style)))
        f.Sizer.Add(tree,1,wx.EXPAND|wx.ALL,0)
        bmp=wx.StaticBitmap(f,size=(200,300))
        bmp.BackgroundColour=wx.NamedColour('WHITE')
        f.Sizer.Add(bmp,1,wx.EXPAND|wx.ALL,0)
        def findicon(filename):
            for line in file(filename,'rb'):
                if line.startswith('icon:'):
                    _,dst=line.strip().split(':',1)
                    return dst.strip()
        def updpict(evt):
            item=tree.Selection
            try:
                typ,name=tree.GetPyData(item)
            except TypeError:
                return
            fname=os.path.join(src,name)
            if typ=="game":
                fname+='.mse-game'
                icon=os.path.join(fname,"game")
            else:
                fname+='.mse-style'
                icon=os.path.join(fname,"style")
            icon=findicon(icon)
            if icon:
                bmp.ClearBackground()
                #double the image; there are to small.
                img=wx.Image(os.path.join(fname,icon))
                #img=img.Rescale(img.Width*2,img.Height*2)
                bmp.SetBitmap(wx.BitmapFromImage(img))
                f.Layout()
        def OnReadTemplate(evt):
            item=tree.Selection
            try:
                typ,name=tree.GetPyData(item)
            except TypeError:
                return
            from tempfile import mktemp
            fname=mktemp('.tmpl')
            elts=MSE.ImportTemplate(name,dst=fname)
            shapes=dict()
            props=dict()
            for eltName in elts:
                elt=elts[eltName]
                item=self.AddElt(elt)
                blank,shape,page=self.tree.GetPyData(item)
                print "here: should distinguish between script name & game name"
                for pName in elt.params:
                    p=elt.params[pName]
                    page.GetPropertyByName(pName).SetValue(p.value)
                if elt.Type=='template':
                    shape.SetHeight(elt['card height'])
                    shape.SetWidth(elt['card width'])
                    shape.SetX(elt['card width']/2)
                    shape.SetY(elt['card height']/2)
                else:
                    shape.SetHeight(elt['height'])
                    shape.SetWidth(elt['width'])
                    shape.SetX(elt['left']+elt['width']/2)
                    shape.SetY(elt['top']+elt['height']/2)
            self.file = ""
            self.Title="MSE_"+name
            f.Close()
        tree.Bind(wx.EVT_TREE_SEL_CHANGED,updpict)
        tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED,OnReadTemplate)
        bmp.Bind(wx.EVT_LEFT_DCLICK,OnReadTemplate)
        tree.Expand(root)
        f.Show()
        return
    
    def OnCloseWindow(self,evt):
        if self.changed and (not self.saved):
            dlg = wx.MessageDialog(self, "Save changes to current template ?","Save changes ?", wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_YES:
                self.OnSave(evt)
            elif result== wx.ID_CANCEL:
                return
        #Save Last Opened template
        if self.file:
            file('designer_last_file','wb').write(self.file)
            if self.Parent:#load template in mainframe
                self.Parent.LoadTemplate(self.file,select=True,target=self.TemplateTreeItem)
        evt.Skip()
        
    def OnDuplicate(self,evt):
        item=self.tree.Selection
        elt,shape,page=self.tree.GetPyData(item)
        res=dict()
        name=elt.name+'-copy'
        value=page.GetValues()
        res[name]=elt.Type,value
        self.changed=True
        if not self.Title[-1]=='*':
            self.Title+='*'
        self.LoadElements(res)
        
    def OnCenterVElt(self,evt):
        item=self.tree.Selection
        data=self.tree.GetPyData(item)
        if data:
            elt,shape,page=self.tree.GetPyData(item)
            if elt.Type=='template':#Root ! 
                return
            #find y max, y and center....
            xmax=self.elts[0].GetPropertyByName('card height').GetValue()
            x=elt['height']
            elt['top']=(xmax-x)/2
            shape.SetY(elt['top'])
        ##Specific property changes
        self._thewin.Refresh()
     
    def OnCenterHElt(self,evt):
        item=self.tree.Selection
        data=self.tree.GetPyData(item)
        if data:
            elt,shape,page=self.tree.GetPyData(item)
            if elt.Type=='template':#Root ! 
                return
            #find y max, y and center....
            xmax=self.elts[0].GetPropertyByName('card width').GetValue()
            x=elt['width']
            elt['left']=(xmax-x)/2
            shape.SetX(elt['left'])
        ##Specific property changes
        self._thewin.Refresh()
        
    def OnMaxVElt(self,evt):
        item=self.tree.Selection
        data=self.tree.GetPyData(item)
        if data:
            elt,shape,page=self.tree.GetPyData(item)
            if elt.Type=='template':#Root ! 
                return
            #find y max, y and center....
            xmax=self.elts[0].GetPropertyByName('card height').GetValue()
            elt['height']=xmax
            elt['top']=0
            shape.SetY(elt['top']+xmax/2)
            shape.SetHeight(xmax)
            
        ##Specific property changes
        self._thewin.Refresh()
        
    def OnMaxHElt(self,evt):
        item=self.tree.Selection
        data=self.tree.GetPyData(item)
        if data:
            elt,shape,page=self.tree.GetPyData(item)
            if elt.Type=='template':#Root ! 
                return
            #find y max, y and center....
            xmax=self.elts[0].GetPropertyByName('card width').GetValue()
            elt['width']=xmax
            elt['left']=0
            shape.SetWidth(xmax)
            shape.SetX(elt['left']+xmax/2)
        ##Specific property changes
        self._thewin.Refresh()
        
    def OnDelElt(self,evt):
        item=self.tree.Selection
        elt,shape, page=self.tree.GetPyData(item)
        if elt.Type=='template':#Root ! 
            return
        self.changed=True
        if not self.Title[-1]=='*':
            self.Title+='*'
        self.tree.Delete(item)
        #self._thewin.diagram.RemoveShape(shape)
        del self._thewin.shapes[self._thewin.shapes.index(shape)]
        shape.Delete()
        del self.elts[self.elts.index(page)]
        self._thewin.Refresh()
        self.propgrid.RemovePage(page.GetIndex())
        
    def AddElt(self,blank,fromFile=False):
        imgs={
            'Text':self.il.textelt,
            'Image':self.il.imgelt,
            'Staticimage':self.il.imgelt,
            'Choice':self.il.choiceelt,
            'Info':self.il.infoelt,
            'Set':self.il.setelt,
            'Color':self.il.colorelt,
            'Keyword':self.il.keywordelt,
            'Symbols':self.il.symbolelt,
        }

        if blank.Type=="template":#Root style 
            item=self.tree.RootItem
            #Change root item name
            self.tree.SetItemText(item,blank.name)
            X=0
            Y=0
            W=blank['card width']
            H=blank['card height']
        else:#Normal element style
            item=self.tree.AppendItem(self.tree.RootItem,blank.name,image=imgs.get(blank.Type.capitalize(),-1))
            X=blank['left']
            Y=blank['top']
            W=blank['width']
            H=blank['height']
            if not fromFile:
                if blank['left']==0:
                    X=50+self.tree.GetChildrenCount(self.tree.RootItem)*10
                if blank['top']==0:
                    Y=50+self.tree.GetChildrenCount(self.tree.RootItem)*10
        #Normal processing
        shape=self._thewin.MyAddShape(blank,int(X+W/2), int(Y+H/2), W,H)
        shape._treeitem=item
        self._thewin.Refresh()
        #Now create the propgrid page for this element
        page=self.CreatePropGridPage(blank)
        self.elts.append(page)
        self.tree.SetPyData(item, [blank,shape,page])        
        #Select it only at the end, otherwise, callbakc is called without pydata set up
        self.tree.SelectItem(item)
        return item
        
    def OnNew(self,evt):
        if self.changed & (not self.saved):
            dlg = wx.MessageDialog(self, "Save changes to current template ?","Save changes ?", wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_YES:
                self.OnSave(evt)
            elif result== wx.ID_CANCEL:
                return
        self.changed=False
        self.saved=False
        self.elts=list()
        self.CreateTree()
        self.CreateBlankTemplate()
        
    def OnOpen(self ,evt):
        if self.changed & (not self.saved):
            dlg = wx.MessageDialog(self, "Save changes to current template ?","Save changes ?", wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_YES:
                self.OnSave(evt)
            elif result== wx.ID_CANCEL:
                return
        dlg = wx.FileDialog(self, "Choose a template file", self.dir, "", "Template File (*.tmpl)|*.tmpl|All Files(*.*)|*.*", wx.OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                # Your code
                filename=dlg.GetPath()
                self.LoadTemplate(filename)
        finally:
            dlg.Destroy()
        
    def LoadTemplate(self,filename):
        self.changed=False
        self.saved=False
        self.elts=list()
        self.CreateTree()
        import cPickle        
        import os
        from os.path import split,isfile,join
        from config import card_folder
        if not isfile(filename):
            #try relpath
            if isfile(join(card_folder,filename)):
                filename=join(card_folder,filename)
        self.dir=split(filename)[0]
        self.file = filename        
        self.Title=os.path.split(self.file)[-1]+"*"
        if filename.endswith('.tmpl'):

            res=cPickle.load(file(filename,'rb'))
        elif filename.endswith('.bgp'):
            import package
            p=package.Package(filename)
            res=cPickle.load(p.template)
        self.LoadElements(res)
        self.statusbar.SetStatusText('Template %s Loaded !'%filename)

    def LoadElements(self,res):        
        for name in res:
            Type,vs=res[name]
            elt=FieldFromValues(Type,vs)
            elt.name=name
            self.AddElt(elt,fromFile=True)
            p=self.elts[-1]
            for cname in vs:
                p.GetPropertyByName(cname).SetValue(vs[cname])
  
    def OnSaveAs(self,evt):
        old_file=self.file
        self.file=""
        res=self.OnSave(evt)
        if res==wx.ID_CANCEL:
            self.file=old_file
        
    def OnSave(self,evt):
        safe_title=self.Title
        if self.Title[-1]=='*':
            safe_title=self.Title[:-1]
        if not self.file:
            import os
            dlg = wx.FileDialog(self, message="Choose a destination file", defaultFile=safe_title,defaultDir=self.dir,wildcard="Template File (*.tmpl)|*.tmpl|All Files(*.*)|*.*",style=wx.SAVE | wx.OVERWRITE_PROMPT)
            # Show the dialog and retrieve the user response. If it is the OK response, 
            # process the data.
            if dlg.ShowModal() == wx.ID_OK:
                # This returns a Python list of files that were selected.
                self.file=dlg.GetPath()
                from os.path import split
                self.dir=split(self.file)[0]
                dlg.Destroy()
            else:
                return wx.ID_CANCEL
        self.changed=False
        self.saved=True
        import os.path
        filename=os.path.split(self.file)[-1]
        if not filename.endswith('.tmpl'):
            filename+='.tmpl'
        self.Title=filename
        #Pickle some dict in here !
        from collections import OrderedDict
        res=OrderedDict()
        pg,tb=self.propgrid.GetChildren()
        for i in range(len(self.elts)):
            pname=tb.GetToolByPos(i).Label
            pvalues=self.elts[i].GetValues()
            res[pname]=self.elts[i].Type,pvalues        
        import cPickle
        cPickle.dump(res,file(self.file,'wb'))
        self.statusbar.SetStatusText('Template Saved to %s'%self.file)
        #Now, it applicable, change it on parnet Frame
        if self.file:
            file('designer_last_file','wb').write(self.file)
            if self.Parent:#load template in mainframe
                self.Parent.LoadTemplate(self.file,select=True,target=self.TemplateTreeItem)
        
    def OnMSEExport(self,evt,startfile=True):
        skipped_list=("Set","StaticImage")
        import os, os.path, MSE
        from widgets import FieldFromValues
        safe_title=self.Title
        if self.Title[-1]=='*':
            safe_title=self.Title[:-1]
        if not self.file:
            import os
            dlg = wx.DirDialog(self, "Choose a destination directory for Template Export:", style=wx.DD_DEFAULT_STYLE, defaultPath=self.dir)

            # If the user selects OK, then we process the dialog's data.
            # This is done by getting the path data from the dialog - BEFORE
            # we destroy it. 
            if dlg.ShowModal() == wx.ID_OK:
                path=dlg.GetPath()
                self.dir=path
                # Only destroy a dialog after you're done with it.
                dlg.Destroy()
            else:
                return
        else:
            path=os.path.split(self.file)[0]
        objs=self.elts
        tmp=objs[0]
        name=tmp.GetValues()['short name']
        sname=tmp.GetValues()['style short name']
        pg=os.path.join(path,'%s.mse-game'%name)
        ps=os.path.join(path,'%s-%s.mse-style'%(name,sname))
        if not os.path.isdir(pg):
            os.mkdir(pg)
        if not os.path.isdir(ps):
            os.mkdir(ps)
        game_parts=[]
        style_parts=[]
        for page in objs:
            #MSE.CopyImage(page,pg,ps)
            if page.Type in skipped_list:
                continue
            _obj=FieldFromValues(page.Type,page)
            game_parts.append(obj.export('game').encode('cp1252'))
            style_parts.append(obj.export('style').encode('cp1252'))
            MSE.CopyImage(page,pg,ps)
        file(os.path.join(pg,'game'),'wb').write(os.linesep.join(game_parts))
        file(os.path.join(ps,'style'),'wb').write(os.linesep.join(style_parts))
        if startfile:
            os.startfile(path)
            self.statusbar.SetStatusText('Template Exported!')        
        
    def UpdateInfo(self):
        item=self.tree.Selection
        if item is None:
            return
        if item is self.tree.RootItem:
            self.propgrid.SelectPage(0)
            return
        res=self.tree.GetPyData(item)
        if res is None:
            return
        elt,shape,page=res
        self.propgrid.SelectPage(page)
        #Deal with non visual item like Set
        if page.Type in ('Set','Info'):
            return
        names=['height','width']
        #Name
        p=page.GetPropertyByName('name')
        if elt.Type=="template":
            names=['card height','card width']
            p=page.GetPropertyByName('short name')
        p.SetValue(shape.text)
        #Set Width & Heightstuff
        funcs=[shape.GetHeight,shape.GetWidth]
        for n,f in zip(names,funcs):
            p=page.GetPropertyByName(n)
            p.SetValue(int(f()))
            elt[n]=int(f())
        if elt.Type!='template':
            #Top & Left
            p=page.GetPropertyByName("top")
            v=int(shape.GetY()-shape.GetHeight()/2)
            p.SetValue(v)
            elt['top']=v
            p=page.GetPropertyByName('left')
            v=int(shape.GetX()-shape.GetWidth()/2)
            p.SetValue(v)
            elt['left']=v

    def OnGenSet(self):
        import MSE
        dlg = wx.DirDialog(self, "Choose directory for Sets:", style=wx.DD_DEFAULT_STYLE, defaultPath=self.dir)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                # Your code
                dst_dir=dlg.GetPath()
                self.GenerateSetFiles(dst_dir)
                self.statusbar.SetStatusText('Generation completed!')
        finally:
            dlg.Destroy()
        import os
        os.startfile(dst_dir)
    
    def GenerateSetFiles(self,dst_dir):
        #self.dir=dst_dir
        import MSE
        return MSE.GenerateSetFiles(self.elts,dst_dir,startfile=False)
        
    def OnPyShell(self,evt):
        if self.pycrust:
            return
        wx.BeginBusyCursor()
        import wx.py.shell as s
        import wx.lib.agw.aui as aui
        self.pycrust=s.Shell(self,locals={'frame':self})
        self._mgr.AddPane(self.pycrust,aui.AuiPaneInfo().Name('Shell').Caption('Shell').Bottom().Layer(1).MaximizeButton(True).MinimizeButton(True).CloseButton(False).MinimizeMode(aui.AUI_MINIMIZE_POS_LEFT))
        self._mgr.Update()
        wx.EndBusyCursor()
        
    def OnStartMSE(self,evt):
        import os.path
        from os.path import join
        from config import MSE_PATH
        if not os.path.isfile(MSE_PATH):
            dlg = wx.FileDialog(self, "Where is MSE ?", self.dir, "", "All Files(*.*)|*.*", wx.OPEN)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    # Your code
                    filename=dlg.GetPath()
                    import config
                    config.MSE_PATH=MSE_PATH=filename
                    config.set('mse','path',MSE_PATH)
            finally:
                dlg.Destroy()
        from os import startfile
        startfile(MSE_PATH)
        
if __name__=='__main__':
    FrameType=wx.Frame
    f=WYSIFrame(None,startOldFile=True)
    f.Show()
    import sys
    if len(sys.argv)>1 :#filename of a deck ?? load it ! 
        name=sys.argv[1]
        if name.endswith('.tmpl') :
            #print 'Loading Deck ',name
            #remove existing first page
            f.CreateTree()
            f.LoadTemplate(name)
    app.MainLoop()