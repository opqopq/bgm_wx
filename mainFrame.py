#Boa:Frame:MainFrame

import wx
import wx.aui
import  wx.lib.filebrowsebutton as filebrowse
import wx.lib.agw.buttonpanel as bp
import os
from os.path import join

from config import card_folder,print_size
import config

from propgrid import CustomPropertyGrid
from deckmvc import DeckGrid
from actions import TemplateDirectory


[wxID_MAINFRAMEFILEMENUIDNEW, wxID_MAINFRAMEFILEMENUIDOPEN, 
 wxID_MAINFRAMEFILEMENUIDQUIT, wxID_MAINFRAMEFILEMENUIDSAVE, 
 wxID_MAINFRAMEFILEMENUIDSAVEAS, wxID_EXPORT,wxID_MAINFRAMEEDITMENUIDDIR, 
 wxID_MAINFRAMEEDITMENUIDEXPORT, wxID_MAINFRAMEEDITMENUIDPRINT, 
  wxID_MAINFRAMEEDITMENUIDFIT,wxID_PRINT_FORMAT,wxID_PYSHELL, wxID_PYBROWSER, wxID_PACKAGE,
  wxID_PLUGINS, wxID_APPENDDECK,wxID_ADDCARD,wxID_UPDATECARD,wxID_DELETECARD,wxID_EXPORTCARD,wxID_FORMARTCARD
] = [wx.NewId() for _init_coll_filemenu_Items in range(21)]
      
class MainFrame(wx.Frame):
    def _init_coll_editmenu_Items(self, parent):
        parent.Append(help=u'Format deck for printing', id=wxID_MAINFRAMEEDITMENUIDPRINT, kind=wx.ITEM_NORMAL,text=u'&Format for Printing')
        parent.AppendSeparator()
        parent.Append(help='Choose Card Size', id=wxID_MAINFRAMEEDITMENUIDFIT, kind=wx.ITEM_NORMAL, text=u'&Setup Fit Format')
        parent.AppendSeparator()
        parent.Append(help='', id=wxID_EXPORT, kind=wx.ITEM_NORMAL, text=u'&Export to excel\tCTRL-E')
        parent.Append(help='Choose Img Format', id=wxID_PRINT_FORMAT, kind=wx.ITEM_NORMAL, text=u'&Setup Print Img Format')
        parent.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.OnEditmenuIdprintMenu, id=wxID_MAINFRAMEEDITMENUIDPRINT)
        self.Bind(wx.EVT_MENU, self.OnEditmenuIdFitFormat, id=wxID_MAINFRAMEEDITMENUIDFIT)              
        self.Bind(wx.EVT_MENU, self.OnEditMenuPrintFormat, id=wxID_PRINT_FORMAT)
    
    def _init_coll_filemenu_Items(self, parent):
        parent.Append(help='', id=wxID_MAINFRAMEFILEMENUIDNEW, kind=wx.ITEM_NORMAL, text=u'&New Deck')
        parent.Append(help='', id=wxID_MAINFRAMEFILEMENUIDOPEN, kind=wx.ITEM_NORMAL, text=u'&Open Deck')
        parent.Append(help='', id=wxID_APPENDDECK, kind=wx.ITEM_NORMAL, text=u'&Append Deck content ')
        parent.Append(help='', id=wxID_MAINFRAMEFILEMENUIDSAVE, kind=wx.ITEM_NORMAL, text=u'&Save Current Deck')
        parent.Append(help='', id=wxID_MAINFRAMEFILEMENUIDSAVEAS, kind=wx.ITEM_NORMAL, text=u'Save &As')
        parent.AppendSeparator()
        parent.Append(help=u'', id=wxID_MAINFRAMEFILEMENUIDQUIT, kind=wx.ITEM_NORMAL, text=u'&Quit')
        self.Bind(wx.EVT_MENU, self.OnFilemenuIdquitMenu, id=wxID_MAINFRAMEFILEMENUIDQUIT)
        self.Bind(wx.EVT_MENU, self.OnFilemenuIdopenMenu, id=wxID_MAINFRAMEFILEMENUIDOPEN)
        self.Bind(wx.EVT_MENU, self.OnFilemenuIdAppendMenu, id=wxID_APPENDDECK)
        self.Bind(wx.EVT_MENU, self.OnFilemenuIdsaveasMenu, id=wxID_MAINFRAMEFILEMENUIDSAVEAS)
        self.Bind(wx.EVT_MENU, self.OnFilemenuIdnewMenu, id=wxID_MAINFRAMEFILEMENUIDNEW)
        self.Bind(wx.EVT_MENU, self.OnFilemenuIdsaveMenu, id=wxID_MAINFRAMEFILEMENUIDSAVE)
        
    def _init_coll_toolsmenu_Items(self,parent):
        parent.Append(wxID_MAINFRAMEEDITMENUIDEXPORT,"Export Current Image")
        self.Bind(wx.EVT_MENU, self.OnExportCardButton, id=wxID_MAINFRAMEEDITMENUIDEXPORT)
        parent.Append(wxID_PYBROWSER,"Browse BGG")
        self.Bind(wx.EVT_MENU, self.OnBrowseButton, id=wxID_PYBROWSER)
        parent.Append(wxID_PACKAGE,"Create Package")
        self.Bind(wx.EVT_MENU, self.OnCreatePackage, id=wxID_PACKAGE)
        parent.Append(help='Plugins Browser',id=wxID_PLUGINS,kind=wx.ITEM_NORMAL,text="Browse Pl&ugins")
        self.Bind(wx.EVT_MENU, self.OnPluginPanel, id=wxID_PLUGINS)
        parent.AppendSeparator()
        parent.Append(help='Start PyShell',id=wxID_PYSHELL,kind=wx.ITEM_NORMAL,text="&PyShell")
        self.Bind(wx.EVT_MENU, self.OnPyShell, id=wxID_PYSHELL)

    def _init_utils(self):
        # generated method, don't edit
        self.menuBar1 = wx.MenuBar()
        self.filemenu = wx.Menu(title=u'')
        self.editmenu = wx.Menu(title=u'')
        self.toolsmenu = wx.Menu(title=u'')
        self.menuBar1.Append(menu=self.filemenu, title=u'&File')
        self.menuBar1.Append(menu=self.editmenu, title=u'&Edit')
        self.menuBar1.Append(menu=self.toolsmenu, title=u'&Tools')
        self._init_coll_filemenu_Items(self.filemenu)
        self._init_coll_editmenu_Items(self.editmenu)
        self._init_coll_toolsmenu_Items(self.toolsmenu)
    
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=-1, parent=prnt, style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE, title=u'Card Maker')
        self._init_utils()
        self.SetClientSize(wx.Size(660, 572))
        self.SetMenuBar(self.menuBar1)
        self.Bind(wx.EVT_SIZE, self.OnMainFrameSize)
        #Icon
        favicon = wx.Icon('img/favicon.ico', wx.BITMAP_TYPE_ICO, 16, 16)
        self.SetIcon(favicon)        
        self.statusBar1 = self.CreateStatusBar(2, style=wx.ST_SIZEGRIP)

        self.cardbackground=wx.ScrolledWindow(self)
        self.cardbackground.BackgroundColour=wx.Colour(192,192,192)
        self.cardbackground.Sizer=wx.WrapSizer()
        self.cardbackground.Bind(wx.EVT_SIZE, self.OnMainFrameSize)

        self.card = wx.StaticBitmap(self.cardbackground,-1,bitmap=wx.NullBitmap, size=wx.Size(330, 525))
        self.cardbackground.SetScrollbars(20,20,55,40)
        self.card.Bind(wx.EVT_LEFT_DCLICK, self.OnCardLeftDclick)

        self.dir = wx.TreeCtrl(id=-1, parent=self, size=wx.Size(150, 100), style=wx.TR_HAS_BUTTONS|wx.TR_MULTIPLE)
        #Image list
        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        il.fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        il.fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
        il.fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
        il.scriptidx     = il.Add(wx.Bitmap('img/script_icon.png'))
        il.imglidx     = il.Add(wx.Bitmap('img/Image_small.png'))        
        il.dcklidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_REPORT_VIEW, wx.ART_OTHER ,isz))        
        il.templidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_LIST_VIEW, wx.ART_OTHER ,isz))        
        il.packageidx     = il.Add(wx.Bitmap('img/package.png'))       
        self.il=il
        self.dir.SetImageList(il)        
        self.dir.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnDirTreeItemExpanding)#,id=wxID_MAINFRAMEDIR)
        self.dir.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnDirTreeItemActivated)#,id=wxID_MAINFRAMEDIR)
        self.dir.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnDirTreeSelChanged)#,id=wxID_MAINFRAMEDIR)
        
        #Panel with card add options
        self.cardAddOptions=wx.Panel(self)
        self.cardAddOptions.BackgroundColour=wx.NamedColour('WHITE')    
        fgs1 = wx.FlexGridSizer(cols=2, vgap=0, hgap=0)
        

        self.spin = wx.SpinCtrl(self.cardAddOptions,-1, initial=1, max=1000, min=1,style=wx.SP_WRAP | wx.SP_ARROW_KEYS)

             
        self.dual= wx.CheckBox(self.cardAddOptions, -1, "Verso")
        self.dual.SetBackgroundColour(wx.Colour(255,255,255))

        self.rotated= wx.CheckBox(self.cardAddOptions, -1, "Clockwise")
        self.rotated.SetBackgroundColour(wx.Colour(255,255,255))
        self.rotated.Bind(wx.EVT_CHECKBOX, self.OnRotate)
        
        self.fit= wx.CheckBox(self.cardAddOptions,-1)
        
        ls=("Qt:","Dual:","Size:","Rotated:")
        os=(self.spin,self.dual,self.fit,self.rotated)
        for l,o in zip(ls,os):
            label = wx.StaticText(self.cardAddOptions, -1, l)
            fgs1.Add(label, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 15)
            fgs1.Add(o, 1, wx.ALIGN_RIGHT|wx.EXPAND|wx.ALL, 3)
        self.cardAddOptions.SetSizer( fgs1 )
        self.cardAddOptions.SetAutoLayout(1)
        self.cardAddOptions.Size=wx.Size(100,120)
        
        self.actions=wx.TreeCtrl(id=-1, size=(150,100),parent=self, style=wx.TR_HAS_BUTTONS)
        self.actions.SetImageList(il)  
        res=self.actions.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActionsTreeItemActivated)
        res=self.actions.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnActionsTreeSelChanged)
        
        #self.values=wx.TextCtrl(self,-1,size=wx.Size(150,30))
                
        self.propgrid=CustomPropertyGrid(self)
        
        ##Info bar for communication
        self.info = wx.InfoBar(self)
        
        #Editable listbox for creating custom composite template
        ##self.elb= wx.gizmos.EditableListBox(self,-1,"Composite Template")
        
        #New Custom Deck Grid
        self.deckgrid=DeckGrid(self)
        
        #Accelerator table
        aTable = wx.AcceleratorTable([
                            (wx.ACCEL_CTRL,  wx.WXK_ADD, wxID_ADDCARD),
                            #(wx.ACCEL_NORMAL, wx.WXK_DELETE, wxID_DELETECARD),
                            (wx.ACCEL_ALT, ord('A'), wxID_ADDCARD),
                            (wx.ACCEL_ALT, ord('D'), wxID_DELETECARD),
                            (wx.ACCEL_ALT, ord('E'), wxID_EXPORTCARD),
                            (wx.ACCEL_CTRL, wx.WXK_RETURN, wxID_UPDATECARD),
                            (wx.ACCEL_CTRL, ord('P'), wxID_FORMARTCARD),
                            (wx.ACCEL_CTRL, ord('N'), wxID_MAINFRAMEFILEMENUIDNEW),
        ])
        self.SetAcceleratorTable(aTable)
        
    def _init_aui(self):
        import wx.lib.agw.aui as aui
        self._mgr=aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        
        self._mgr.AddPane(self.deckgrid, aui.AuiPaneInfo().Name("deckgrid").Caption("DeckGrid").Bottom().MaximizeButton(True).MinimizeButton(True).CloseButton(False).MinimizeMode(aui.AUI_MINIMIZE_POS_LEFT|aui.AUI_MINIMIZE_CAPT_SMART))
        self._mgr.AddPane(self.dir, aui.AuiPaneInfo().Name("library").Caption("Card Library").Left().MaximizeButton(True).MinimizeButton(True).CloseButton(False).MinimizeMode(aui.AUI_MINIMIZE_CAPT_SMART))
        ##self._mgr.AddPane(self.elb, aui.AuiPaneInfo().Name("composite").Caption("Composite Transformation").Bottom().CloseButton(True).MaximizeButton(True))
        self._mgr.AddPane(self.actions, aui.AuiPaneInfo().Name("Plugins").Caption("Plugins").Right().MaximizeButton(True).MinimizeButton(True).CloseButton(False).MinimizeMode(aui.AUI_MINIMIZE_CAPT_SMART))
        self._mgr.AddPane(self.propgrid, aui.AuiPaneInfo().Name("Options").Caption("Options").Right().MinimizeButton(True).CloseButton(False).MinimizeMode(aui.AUI_MINIMIZE_CAPT_SMART))
        self._mgr.AddPane(self.cardAddOptions,aui.AuiPaneInfo().Name('Card Options').Caption('Card Options').Left().MinimizeButton(True).CloseButton(False).MinimizeMode(aui.AUI_MINIMIZE_CAPT_SMART))
        #self._mgr.AddPane(self.CreateToolbar(), aui.AuiPaneInfo().Name("Buttonbar").Caption("Button Toolbar").ToolbarPane().Layer(1).Top())
        self._mgr.AddPane(self.titleBar, aui.AuiPaneInfo().Name("toolbar").Top().CloseButton(False).MaximizeButton(False).GripperTop(False).Floatable(False).CaptionVisible(False))
                
        #main
        self._mgr.AddPane(self.cardbackground, aui.AuiPaneInfo().Name("cbackground").Caption("Card Image").Center().CloseButton(False).MaximizeButton(True))
        self._mgr.Update()
    
    def CreateToolbar(self):
        ##Image list
        isz = (48,48)
        il = wx.ImageList(isz[0], isz[1])
        il.add     = il.Add(wx.Bitmap('img/tbadd.png'))
        il.update     = il.Add(wx.Bitmap('img/tbupdate.png'))        
        il.export     = il.Add(wx.Bitmap('img/tbexport.png'))       
        il.delete     = il.Add(wx.Bitmap('img/tbdelete.png'))       
        il.pprint     = il.Add(wx.Bitmap('img/tbprint.png'))    
        il.bgg         =il.Add(wx.Bitmap('img/bgg.jpg'))
        il.debug   =il.Add(wx.Bitmap('img/debug.png'))
        il.plugins   =il.Add(wx.Bitmap('img/plugins.png'))
        
        
        self.titleBar = bp.ButtonPanel(self, -1, "Board Game Maker",agwStyle=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)
        self.titleBar.Size=wx.Size(750,-1)
        self.titleBar.SetMinSize(self.titleBar.Size)
        self.titleBar.SetInitialSize(wx.Size(2000,66))
   
        
        #Game ID Field
        bmps=[il.add,il.update,il.export,il.delete,il.pprint]
        shs=["Add","Update","Export","Delete","Print",]
        ids=wxID_ADDCARD,wxID_UPDATECARD,wxID_EXPORTCARD,wxID_DELETECARD,wxID_FORMARTCARD
        lhs=["Add card to deck","Update current deck card","Export selected card to image format","Delete selected card",'Format deck to sheets of cards']
        cbs=[self.OnAddCardButton,self.OnUpdateCardButton,self.OnExportCardButton,self.OnDeleteCardButton,self.OnEditmenuIdprintMenu,self.OnBrowseButton]
        
        for bmp,shortHelp,longHelp,cb,_id in zip(bmps,shs,lhs,cbs,ids):        
            btn = bp.ButtonInfo(self.titleBar, _id,il.GetBitmap(bmp),shortHelp=shortHelp, longHelp=longHelp)
            self.titleBar.AddButton(btn)
            self.Bind(wx.EVT_BUTTON, cb,id=_id)
        
        btn=bp.ButtonInfo(self.titleBar,wxID_PYBROWSER,il.GetBitmap(il.bgg),shortHelp='BGG Browser', longHelp='Browse BGG content', kind=wx.ITEM_CHECK)
        self.titleBar.AddButton(btn)
        self.Bind(wx.EVT_BUTTON,self.OnBrowseButton,id=wxID_PYBROWSER)
        btn=bp.ButtonInfo(self.titleBar,wxID_PLUGINS,il.GetBitmap(il.plugins),shortHelp='Plugins', longHelp='Browse local plugins', kind=wx.ITEM_CHECK)
        self.titleBar.AddButton(btn)
        self.Bind(wx.EVT_BUTTON,self.OnPluginPanel,id=wxID_PLUGINS)
        btn=bp.ButtonInfo(self.titleBar,wxID_PYSHELL,il.GetBitmap(il.debug),shortHelp='Debug', longHelp='Launch  debug console', kind=wx.ITEM_CHECK)
        self.titleBar.AddButton(btn)
        self.Bind(wx.EVT_BUTTON,self.OnPyShell,id=wxID_PYSHELL)        
        
        self.titleBar.DoLayout()
        return self.titleBar
        
    def OnCreatePackage(self,evt):
        dlg = wx.DirDialog(self,defaultPath='.')
        wx.BeginBusyCursor()
        try:
            if dlg.ShowModal() == wx.ID_OK:
                dir = dlg.GetPath()
                import os.path
                base,dirname=os.path.split(dir)
                dst=os.path.join(base,dirname+'.bgp')
                # Your code
                wx.BeginBusyCursor()
                import package
                p=package.Package.fromFolder(dir,dst)
                wx.EndBusyCursor()
                self.statusBar1.SetStatusText('Package Created !')
                import os
                if hasattr(os,'startfile'):
                    os.startfile(base)
                self.LoadTemplate(dst,select=False)
        finally:
            dlg.Destroy()
        wx.EndBusyCursor()
            
    def OnPyShell(self,evt):
        import wx.lib.agw.aui as aui
        if evt.EventObject._toggle:
            if self.pycrust:
                return
            wx.BeginBusyCursor()
            import wx.py.shell as s
            self.pycrust=s.Shell(self,locals={'frame':self})
            self._mgr.AddPane(self.pycrust,aui.AuiPaneInfo().Name('Shell').Caption('Shell').Bottom().Layer(1).MaximizeButton(True).MinimizeButton(False).CloseButton(False).MinimizeMode(aui.AUI_MINIMIZE_POS_LEFT).DestroyOnClose(True))
            self._mgr.Update()
            wx.EndBusyCursor()
        else:
            self._mgr.ClosePane(self._mgr.GetPane('Shell'))
            self._mgr.Update()
            self.pycrust=None
            
    def OnPluginPanel(self,evt):
        if evt.EventObject._toggle:
            if self.pluginpanel:
                return
            wx.BeginBusyCursor()
            import wx.lib.agw.aui as aui
            from pluginpanel import PluginPanel
            self.pluginpanel=PluginPanel(self)
            self._mgr.AddPane(self.pluginpanel,aui.AuiPaneInfo().Name('plugins').Caption('Plugins Library').Right().Layer(1).MaximizeButton(True).MinimizeButton(False).CloseButton(False).MinimizeMode(aui.AUI_MINIMIZE_CAPT_SMART).DestroyOnClose(True))
            self._mgr.Update()
            wx.EndBusyCursor()
        else:
            self.pluginpanel=None
            self._mgr.ClosePane(self._mgr.GetPane('plugins'))
            self._mgr.Update()

    def __init__(self, parent):
        self.pycrust=None
        self.bggbrowser=None
        self.pluginpanel=None
        self.currentcard=''
        self._init_ctrls(parent)
        self.CreateToolbar()
        self._init_aui()
        #default valuie
        self.spin.SetValue(1)
        self.deckname="None"
        #Fullfill the card dir
        self.root=self.dir.AddRoot("Cards")
        self.FillDir()
        self.dir.Expand(self.root)
        #End of Boa
        self.SetDropTarget(MyFileDropTarget(self))
        #Create handler on cards
        self.deckdir=config.get('user','deckdir')
        if self.deckdir is None:
            self.deckdir="."
        h,w=self.fitting_size=print_size
        self.fit.Label='%sx%s'%(h,w)
        self.fit.Value=True
        #Create registry for template & scripts :
        self.templates=TemplateDirectory()
        self.scripts=dict()
        #Build Actions Tree
        self.BuildActionTree() 
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        #Import existing file
        import os.path
        if os.path.isfile('last_opened_file_bgm'):
            path=file('last_opened_file_bgm').read()
            if os.path.isfile(path):
                self.LoadDeck(path)
            elif os.path.isfile(os.path.join(card_folder,path)):
                self.LoadDeck(os.path.join(card_folder,path))
        
    def OnCloseWindow(self,evt):
        #Unbind some evtbinder to prevent some mistaken callbacks
        self.actions.Unbind(wx.EVT_TREE_SEL_CHANGED)
        #Save current opened file & current perspective
        d,f=self.deckdir,self.deckname
        import os.path
        if d.startswith(card_folder):
            d=os.path.relpath(d,card_folder)
        file('last_opened_file_bgm','wb').write(os.path.join(d,f))
        evt.Skip()
        
    def BuildActionTree(self):
        #Fill the Actions Dir
        self.aroot=self.actions.AddRoot("Packages:")
        import plugins
        from os.path import join
        for fname in plugins.autoload:
            self.LoadTemplate(join('plugins',fname))
        self.actions.Expand(self.aroot)

    def FillDir(self):
        import os
        global card_folder
        if card_folder is None:
            import config
            dlg = wx.DirDialog(self, "Choose a folder containg cards pictures:",style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    folder = dlg.GetPath()
                    # Your code
                    config.card_folder=folder
                    config.set('card','src',folder)
            finally:
                dlg.Destroy()
            card_folder=folder
        #Now for the fullfill
        dirs=os.listdir(card_folder)
        for d in sorted(dirs):
            if not os.path.isdir(join(card_folder,d)):
                continue
            child=self.dir.AppendItem(self.root,d)
            self.dir.SetPyData(child,('dir',d))
            self.dir.SetItemImage(child, self.il.fldridx, which=wx.TreeItemIcon_Normal)
            self.dir.SetItemImage(child, self.il.fldropenidx, which=wx.TreeItemIcon_Expanded)  
            self.dir.SetItemHasChildren(child,True)
        
    def OnDirTreeItemExpanding(self, event):
        item=event.GetItem()
        if item == self.root:
            return True
        #Test for lazyness
        if self.dir.GetFirstChild(item)[0].IsOk():
            return
        typ,path=self.dir.GetPyData(item)
        if typ=="dir":
            haschild=False
            dirs=sorted([x.lower() for x in os.listdir(join(card_folder,path))])
            for d in dirs:
                if os.path.isdir(join(card_folder,join(path,d))):
                    child=self.dir.AppendItem(item,d)
                    self.dir.SetPyData(child,('dir',join(path,d)))
                    self.dir.SetItemImage(child, self.il.fldridx, which=wx.TreeItemIcon_Normal)
                    self.dir.SetItemImage(child, self.il.fldropenidx, which=wx.TreeItemIcon_Expanded)  
                    self.dir.SetItemHasChildren(child,True)
                    haschild=True                    
                elif os.path.splitext(d)[-1].lower() in ['.jpg','.jpeg','.png','.gif','.bmp' ]:
                    child=self.dir.AppendItem(item,d)
                    self.dir.SetPyData(child,('card',join(path,d)))
                    self.dir.SetItemImage(child,self.il.imglidx)
                    haschild=True
                elif os.path.splitext(d)[-1].lower() in ['.tmpl']:
                    child=self.dir.AppendItem(item,d)
                    self.dir.SetPyData(child,('template',join(path,d)))
                    self.dir.SetItemImage(child,self.il.templidx)
                    haschild=True
                elif os.path.splitext(d)[-1].lower() in ['.bgp']:
                    child=self.dir.AppendItem(item,d)
                    self.dir.SetPyData(child,('package',join(path,d)))
                    self.dir.SetItemImage(child,self.il.packageidx)
                    haschild=True                    
                elif os.path.splitext(d)[-1].lower() in ['.csv']:
                    child=self.dir.AppendItem(item,d)
                    self.dir.SetPyData(child,('deck',join(path,d)))
                    self.dir.SetItemImage(child,self.il.dcklidx)
                    haschild=True                                        
            self.dir.SetItemHasChildren(item,haschild)                    
            
    def OnDirTreeItemActivated(self, event):
        item=event.GetItem()
        #Double clicking on the root make the tree emptying itself
        if item == self.root:
            self.dir.DeleteAllItems()
            self.root=self.dir.AddRoot("Cards")
            self.FillDir()
            self.dir.Expand(self.root)
            return
        typ,path=self.dir.GetPyData(item)
        if typ=='card':
            self.AddCard(qt=1)
        elif typ in ("template",'package'):
            #load it
            from os.path import join
            p=join(card_folder.decode('cp1252'),path.encode('cp1252'))
            self.LoadTemplate(p,select=True)
        elif typ=="deck":
            from os.path import join
            p=join(card_folder.decode('cp1252'),path.encode('cp1252'))
            self.LoadDeck(p)
        elif typ=='dir':
            wx.BeginBusyCursor()
            self.OnDirTreeItemExpanding(event)#add children
            dlg = wx.MessageDialog(self, 'Add All Cards from folder (%d)?'%(self.dir.GetChildrenCount(item)),'Confirmation', wx.YES_NO | wx.ICON_QUESTION)
            try:
                res=dlg.ShowModal()
                if res==wx.ID_YES:
                    c,cookie=self.dir.GetFirstChild(item)
                    while c.IsOk():
                        t,p=self.dir.GetPyData(c)
                        if t=='card':
                            #self.SetCard(p)
                            #self.AddCard(qt=1)
                            self.AddCard(cardPath=p,qt=1)
                        c,cookie=self.dir.GetNextChild(item,cookie)
            finally:
                wx.EndBusyCursor()
                dlg.Destroy()
                
    def OnActionsTreeSelChanged(self, event):
        item=self.actions.Selection
        if not item.IsOk():
            return
        data=self.actions.GetPyData(item)
        if data :
            typ,fun=data
            #First build property page
            self.propgrid.Build(fun)
            #Check if there is a change of template :
            if typ in ('template','package') :
                self.SetCard(template=fun.name)
            self.statusBar1.SetStatusText(fun.help)
        else:
            #IF not data, it is a dir=> change that to "no template"
            self.SetCard(template="Empty")
                
    def OnActionsTreeItemActivated(self, event):
        item=event.GetItem()
        #chekc if refresh is needed
        if item ==self.aroot:
            self.actions.DeleteAllItems()
            self.BuildActionTree()
            return
        _data=self.actions.GetPyData(item)
        if _data:
            typ,elt=self.actions.GetPyData(item)
            if typ=='script':#execute it with self as an input
                d = self.propgrid.GetCurrentPage().GetPropertyValues()
                wx.BeginBusyCursor()
                try:
                    elt.run(self,values=d)
                except Exception,e:
                    import traceback
                    traceback.print_exc()
                wx.EndBusyCursor()
            elif typ in ("template"):
                if elt.isTemplate:
                    import designer
                    f=designer.WYSIFrame(self,target=item)
                    f.Show()
                    f.LoadTemplate(elt.name)
            
    def LoadTemplate(self,name,select=False,target=None):
        #print 'loading',name
        fname=os.path.splitext(os.path.split(name)[-1])[0]
        pr=None
        _vars=dict()
        if name.endswith('.tmpl'):
            _vars['template_%s'%fname]=self.templates.get(name)
        elif name.endswith('.py'):
            if not os.path.isfile(name):
                print "[warn] file does not exist:",name
                return
            execfile(name,globals(),_vars)
        elif name.endswith('.bgp'):
            from actions import make_template
            tmpl=make_template(name)
            _vars['package_%s'%fname]=tmpl
        else:
            raise ValueError('Do not know what to do with file '+name)
        for name in _vars:
            if name.startswith('template_'):
                if target is None:#Re use existing item to add template
                    if pr is None:
                        pr=self.actions.AppendItem(self.aroot,fname)
                        self.actions.SetItemImage(pr, self.il.fldridx, which=wx.TreeItemIcon_Normal)
                        self.actions.SetItemImage(pr, self.il.fldropenidx, which=wx.TreeItemIcon_Expanded)  
                        self.actions.SetItemHasChildren(pr,True)                    
                    item=self.actions.AppendItem(pr,_vars[name].name)
                    self.actions.SetItemImage(item,self.il.templidx)
                else:#Only works for template that have been double clicked in action tree
                    item=target
                self.actions.SetPyData(item,('template',_vars[name]))
                self.templates[_vars[name].name]=_vars[name]
                if select:
                    #Select the new template item
                    self.OnActionsTreeSelChanged(None)
                    self.actions.ScrollTo(item)
            elif name.startswith('script_'):
                if pr is None:
                    pr=self.actions.AppendItem(self.aroot,fname)
                    self.actions.SetItemImage(pr, self.il.fldridx, which=wx.TreeItemIcon_Normal)
                    self.actions.SetItemImage(pr, self.il.fldropenidx, which=wx.TreeItemIcon_Expanded)  
                    self.actions.SetItemHasChildren(pr,True)
                item=self.actions.AppendItem(pr,_vars[name].name)
                self.actions.SetPyData(item,('script',_vars[name]))
                self.scripts[_vars[name].name]=_vars[name]
                self.actions.SetItemImage(item,self.il.scriptidx)
            elif name.startswith('package_'):
                item=self.actions.AppendItem(self.aroot,_vars[name].name)
                self.actions.SetPyData(item,('package',_vars[name]))
                self.actions.SetItemImage(item,self.il.packageidx)
                self.templates[_vars[name].name]=_vars[name]

    def OnRotate(self,event=None):
        self.SetCard()

    def SetCard(self,path=None, template=None,values=None):
        wx.BeginBusyCursor()
        #Take a path and display it on the self.card image holder
        self.card.SetBitmap(wx.EmptyBitmap(0,0))
        if path is None and self.currentcard:
            path=self.currentcard
        self.currentcard=path
        self.card.Freeze()
        if path:# starting case
            w,h=self.cardbackground.GetSizeTuple()
            W,H=self.card.GetSizeTuple()
            where=join(card_folder.decode('cp1252'),path.encode('cp1252'))
            #If path does not exist, use a blank image
            import os.path
            if not os.path.isfile(where) :
                self.Warn( 'no image found=> blank one')
                img=wx.EmptyImage(*self.fitting_size)
            else:
                img=wx.Image(where)#,wx.BITMAP_TYPE_JPEG)
            ##Templating
            #If the card come from a deck with a template set, apply it. Otherwise, take the current selection
            if template:
                import os.path
                if os.path.isfile(template):
                    from actions import make_template, template_empty
                    t=make_template(template)
                elif template in self.templates:
                    t=self.templates[template]
                else:
                    print '[Warn]: template not existing:',template
                    t=template_empty
                if values is None:
                    _page=self.propgrid.GetPageByName(t.name)
                    if _page==-1:
                        #_page does not exists: build it by selecting the template
                        self.propgrid.Build(t)
                    values= self.propgrid.GetPage(t.name).GetPropertyValues()
                img=t.format(img,values)
            else:
                #If a template exist but is empty (like '') but NOT None, do nothing! 
                #Otherwise, it template IS None, try to grab the currently selected template
                if template is None:
                    if self.actions.Selection:
                            data=self.actions.GetPyData(self.actions.Selection)
                            if data is not None:
                                typ,template=data
                                if typ=="template" :
                                    d = self.propgrid.GetCurrentPage().GetPropertyValues()
                                    img=template.format(img,d)
                                elif typ=="package":
                                    d = self.propgrid.GetCurrentPage().GetPropertyValues()
                                    img=template.format(img,d)                                    
            #If rotation is asked, rotate it clockwise
            if self.rotated.Value:
                img=img.Rotate90()
            ##Simple rescale with aspect ratio for conveniance
            _w,_h=img.GetWidth(), img.GetHeight()
            ratio   = min( float(w)/_w,  float(h)/_h)
            paneinfo= self._mgr.GetPane("cbackground")
            if int(ratio*_w)<_w or int(ratio*_h)<_h:#to big=> rescale
                img = img.Rescale(int(ratio*_w), int(ratio*_h), wx.IMAGE_QUALITY_HIGH)
                paneinfo.Caption("Card Image -(%d%%)"%int(ratio*100))
            else:
                paneinfo.Caption("Card Image")
            self.Refresh()                
            #Now display
            bitmap=img.ConvertToBitmap()
            self.card.SetBitmap(bitmap)
            #data=mana.getInfo(path)
            data=[path]
            self.updateinfo(data)
        self.card.Refresh(False)
        self.card.Thaw()
        wx.EndBusyCursor()
        
    def OnMainFrameSize(self, event):
        event.Skip()
        #print "onsize"
        self.SetCard()

    def OnExportCardButton(self,event):
        "Export the current image as per template Transformation"
        dlg = wx.FileDialog(self, "Choose a destination file for image", self.deckdir, "", "All Files(*.*)|*.*", wx.SAVE| wx.OVERWRITE_PROMPT)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                import os.path
                path,ext=os.path.splitext(filename)
                if ext.lower()==".jpg":
                    ext=".jpeg"
                typ=getattr(wx,"BITMAP_TYPE_"+ext[1:].upper(),None)
                if not typ:
                    print "Reuqested type not existing. Converting to JPEG",
                    typ=wx.BITMAP_TYPE_JPEG
                self.card.GetBitmap().SaveFile(filename, typ)
                    
        finally:
            dlg.Destroy()

    def OnDeleteCardButton(self,event):
        self.deckgrid.DeleteSelections()
        self.deckgrid.OnSelectionChanged(None)
        
    def OnCardLeftDclick(self, event):
        self.AddCard(qt=1)
        
    def AddCard(self,cardPath=None,qt=None, update=False, displayName=None,dual=None,rotated=None,fit=None,template=None,values=None):
        #Default values
        if dual is None:
            dual=self.dual.Value
        if rotated is None:
            rotated= self.rotated.Value
        if fit is None:
            fit=self.fit.Value
        #Are there multiple cards selected ?
        multiple_cards=False
        if cardPath is None:
            cardPath=self.currentcard
            #Keep the pultiples potential selections:
            cardspaths=self.GetSelectedPaths()
            if len(cardspaths)>1:
                multiple_cards=True
        if template is None :
            template=""
            #Get the currently selected template, if any :
            _sel=self.actions.Selection
            if _sel:
                _data=self.actions.GetPyData(self.actions.Selection)
                if _data is not None:
                    if _data[0]=='template':
                        template=_data[1].name
        #Now for the values. No value without template
        _vs=dict()
        if template:
            #If none, the current selection will be inserted 
            #Otherwise, the current selection + the given values will be inserted
            _vs.update(self.propgrid.GetCurrentPage().GetPropertyValues())
            if values is not None:
                _vs.update(values)
        if qt is None:
            qt=self.spin.GetValue()
        d,p=os.path.split(cardPath)
        if displayName is None:
            displayName=os.path.splitext(p)[0]
        #Update or create ? 
        if update:
            from multiupdatepanel import MultiUpdatePanel
            from deckmvc import DeckCard
            newCard=DeckCard(displayName,qt,cardPath,fit,dual,rotated,template,_vs)
            p=MultiUpdatePanel(self,newCard=newCard,oldCard=self.deckgrid.GetSelectedCard())
            #This dialog will handle multi update for me
        else:#Add mode
            #if multiple cards, add them all
            if multiple_cards:
                for sel in cardspaths:
                    d,p=os.path.split(sel)
                    displayName=os.path.splitext(p)[0]
                    self.deckgrid.AppendRow([displayName,qt,sel,fit,dual,rotated,template,_vs])
            else:
                self.deckgrid.AppendRow([displayName,qt,cardPath,fit,dual,rotated,template,_vs])
        self.updateinfo(data=[])
        
    def OnAddCardButton(self, event):
        self.AddCard(update=False)

    def OnUpdateCardButton(self, event):
        items=self.dir.GetSelections()
        if len(items):            
            self.AddCard(update=True)

    def OnFilemenuIdquitMenu(self, event):
        self.Close()
    
    def OnFilemenuIdopenMenu(self, event):
        dlg = wx.FileDialog(self, "Choose a file", self.deckdir, "", "Grid File (*.csv)|*.csv|Deck File (*.dck)|*.dck|All Files(*.*)|*.*", wx.OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                # Your code
                self.LoadDeck(filename)
        finally:
            dlg.Destroy()
            
    def OnFilemenuIdAppendMenu(self, event):
        dlg = wx.FileDialog(self, "Choose a file", self.deckdir, "", "Grid File (*.csv)|*.csv|Deck File (*.dck)|*.dck|All Files(*.*)|*.*", wx.OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                # Your code
                self.LoadDeck(filename,append=True)
        finally:
            dlg.Destroy()
            
    def LoadDeck(self,filename,append=False):
        wx.BeginBusyCursor()
        #        
        self.deckgrid.Load(filename,append)
        self.statusBar1.SetStatusText('Deck Loaded !')
        self.SetTitle(filename)
        self.deckdir,self.deckname=os.path.split(filename)
        config.set('user','deckdir',self.deckdir)
        self.updateinfo(data=[])
        #If deckdir in card folder path, open the tree accordingly
        if self.deckdir.startswith(card_folder):
            path=os.path.relpath(self.deckdir,card_folder)
            def get_item_by_label(self, tree, search_text, root_item):
                item, cookie = tree.GetFirstChild(root_item)
                while item.IsOk():
                    text = tree.GetItemText(item)
                    if text.lower() == search_text.lower():
                        return item
                    if tree.ItemHasChildren(item):
                        match = self.get_item_by_label(tree, search_text, item)
                        if match.IsOk():
                            return match
                    item, cookie = tree.GetNextChild(root_item, cookie)
                return wx.TreeItemId()
            item=self.dir.RootItem
            for step in path.split(os.path.sep):
                item,cookie=self.dir.GetFirstChild(item)
                while item.IsOk():
                    text=self.dir.GetItemText(item)
                    if text.lower()==step.lower().strip():
                        self.dir.Expand(item)
                        break
                    item,cookie=self.dir.GetNextChild(item,cookie)
        #also load actions file, if any :
        _f,_e=os.path.splitext(filename)
        if os.path.isfile(_f+'.py'):
            self.statusBar1.SetStatusText('Deck Loaded - actions script found & loaded !')
            self.LoadTemplate(os.path.join(self.deckdir,_f+'.py'))
        wx.EndBusyCursor()
        
    def SaveDeck(self,filename):
        #~ import cPickle
        #~ deck=self.GetCurrentDeck()
        #~ #New deck style: insert the fiiting sie at the start of the deck
        #~ deck.insert(0,self.fitting_size)
        #~ try:
            #~ cPickle.dump(deck,file(filename,'wb'))
        #~ except Exception,err:
            #~ self.statusBar1.SetStatusText(err)
        #~ else:
        #Second save stuff
        self.deckgrid.Save(filename,self.fitting_size)
        self.statusBar1.SetStatusText('Deck Saved !')
        self.SetTitle(filename)
        self.deckdir,self.deckname=os.path.split(filename)

    def GetCurrentDeck(self):
        return self.deckgrid.model.cards
        
    def OnFilemenuIdsaveMenu(self, event):
        if getattr(self,'deckname',None) and os.path.isfile(join(self.deckdir,self.deckname)):
            self.SaveDeck(join(self.deckdir,self.deckname))
        else:
            self.OnFilemenuIdsaveasMenu(event)

    def OnEditmenuIdprintMenu(self, event):
        #Where to save page ? 
        dlg = wx.DirDialog(self,defaultPath=self.deckdir)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                dir = dlg.GetPath()
                # Your code
                wx.BeginBusyCursor()
                import printer
                printer.format(self.GetCurrentDeck(),dir,self.deckname,fitting_size=self.fitting_size,templates=self.templates)
                wx.EndBusyCursor()
                self.statusBar1.SetStatusText('Formatting Done !')
                import os
                if hasattr(os,'startfile'):
                    os.startfile(dir)
        finally:
            dlg.Destroy()

    def OnFilemenuIdnewMenu(self, event):
        self.currentdeck=dict()
        self.deckgrid.DeleteAllItems()
        self.deckgrid.numrow=0
        self.SetTitle('New Deck - UnSaved')
        self.deckname="new"
        self.updateinfo()
        
    def OnDirTreeSelChanged(self, event):
        item=event.GetItem()
        if item == self.root:
            return True
        typ,card=self.dir.GetPyData(item)
        if typ=='card':
            self.SetCard(card)
            
    def Warn(self,txt,mode='WARNING'):
        print "[WARN]",txt
        if mode=='ERROR':
            self.info.ShowMessage(txt,wx.ICON_ERROR)
        else:
            self.info.ShowMessage(txt,wx.ICON_WARNING)
        
    def updateinfo(self,data=''):
        f,b=self.deckgrid.GetDeckSize(dual=True)
        self.statusBar1.SetStatusText('%d card(s) - %d fronts, %d backs'%(f+b,f,b),1)

    def OnFilemenuIdsaveasMenu(self, event):
        dlg = wx.FileDialog(self, "Choose a file", self.deckdir, "", "*.*", wx.SAVE| wx.OVERWRITE_PROMPT)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                #Add dck ending
                if not filename.endswith('.csv'):
                    filename+='.csv'
                # Your code
                self.SaveDeck(filename)
        finally:
            dlg.Destroy()

    def OnEditmenuIdFitFormat(self, event):
        from fit_siz import GetFSDialog
        dlg=GetFSDialog(self)
        w,h=self.fitting_size
        dlg.SetValues(self.fitting_size)
        if dlg.ShowModal()==wx.ID_OK:
            try:
                w,h=dlg.GetValues()
                self.fitting_size=(int(w),int(h))
                self.fit.Value="%sx%s"%(w,h)
            finally:
                dlg.Destroy()
    
    def OnEditMenuPrintFormat(self, event):
        import config
        choices=['jpg', 'png', 'bmp']
        dlg = wx.SingleChoiceDialog(self, 'Choose Print Image Format', 'Image Type',choices, wx.CHOICEDLG_STYLE)
        dlg.SetSelection(choices.index(config.PRINT_FORMAT))
        if dlg.ShowModal() == wx.ID_OK:
            choice=dlg.GetStringSelection()
            import config
            config.PRINT_FORMAT=choice
            config.set('print','format',choice)
        dlg.Destroy()
            
    def GetCurrentSelectedPath(self):
        items=self.dir.GetSelections()
        if not items:
            return
        sel=items[0]
        _data=self.dir.GetPyData(sel)
        if not _data:
            self.Warn("Select a picture in Libray first !")
            return
        typ,path=_data
        if typ!="card":
            self.Warn("Select a picture in Libray first !")
            return
        return path
    
    def GetSelectedPaths(self):
        res=[]
        items=self.dir.GetSelections()
        for sel in items:
            _data=self.dir.GetPyData(sel)
            if not _data:
                continue
            typ,path=_data
            if typ!="card":
                continue        
            res.append(path)
        return res
    
    def OnBrowseButton(self,evt):
        print evt.EventObject._toggle
        if evt.EventObject._toggle:
            wx.BeginBusyCursor()
            import wx.lib.agw.aui as aui
            if self.bggbrowser:
                return
            from bggbrowser import BGGFrame
            self.bggbrower=BGGFrame(self)
            self._mgr.AddPane(self.bggbrower,aui.AuiPaneInfo().Name('BGGBrowser').Caption('BGGBrowser').MaximizeButton(True).Layer(1).Left().MinimizeButton(False).CloseButton(False).MinimizeMode(aui.AUI_MINIMIZE_CAPT_SMART).DestroyOnClose(True))         
            self._mgr.Update()
            wx.EndBusyCursor()
        else:
            self._mgr.ClosePane(self._mgr.GetPane('BGGBrowser'))
            self._mgr.Update()
            self.bggbrower=None
        
class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, parent):
        wx.FileDropTarget.__init__(self)
        self.parent = parent

    def OnDropFiles(self, x, y, files):
        for f in files:
            if f.endswith('py') or f.endswith('.tmpl') :
                self.parent.LoadTemplate(f,select=True)
                return
            #Else, load it
            self.parent.LoadDeck(f)