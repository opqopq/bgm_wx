"Define a simple panel used for displayed & loading the existing plugins"

import wx
import wx.lib.agw.customtreectrl as CT

class PluginPanel(wx.Panel):
        def __init__(self,parent):
            wx.Panel.__init__(self,parent)
            self.Title="Plugins Browser"
            self.Size=wx.Size(200,800)
            self.Sizer=wx.BoxSizer(wx.VERTICAL)
            #Game ID Field
            self.dirs = CT.CustomTreeCtrl(self)
            self.dirs.AddRoot('Plugins:')
            self.dirs.AssignImageList(self.Parent.il)
            self.root=self.dirs.GetRootItem()
            self.dirs.SetItemImage(self.root, self.Parent.il.fldridx, CT.TreeItemIcon_Normal)
            self.dirs.SetItemImage(self.root, self.Parent.il.fldropenidx, CT.TreeItemIcon_Expanded)
            self.dirs.Bind(CT.EVT_TREE_ITEM_CHECKED,self.OnItemCheck)
            self.Sizer.Add(self.dirs,1,wx.EXPAND|wx.ALL,0)
            #Bottom item
            self.autoreload=wx.CheckBox(self,-1,"Auto Reload template ?")
            self.autoreload.SetValue(True)
            self.Sizer.Add(self.autoreload,0,wx.ALIGN_CENTER_HORIZONTAL,0)
            self.reload=wx.Button(self,-1,"Reload plugins list")
            self.reload.Bind(wx.EVT_BUTTON,self.OnReload)
            self.Sizer.Add(self.reload,0,wx.EXPAND|wx.ALL, 0)
            self.OnReload(None)
            
        def OnItemCheck(self,evt):
            item = evt.GetItem()
            if self.dirs.IsItemChecked(item):
                self.Parent.LoadTemplate(self.dirs.GetPyData(item))
            evt.Skip()
            
        def OnReload(self,evt):
            import os, os.path
            nodes=dict()
            nodes['plugins']=self.dirs.GetRootItem()
            self.dirs.DeleteChildren(self.dirs.GetRootItem())
            for root, dirs, files in os.walk('plugins'):
                for d in dirs:
                    nodes[os.path.join(root,d)]=self.dirs.AppendItem(self.dirs.GetRootItem(),d)
                    self.dirs.SetItemImage(nodes[os.path.join(root,d)], self.Parent.il.fldridx, CT.TreeItemIcon_Normal)
                    self.dirs.SetItemImage(nodes[os.path.join(root,d)], self.Parent.il.fldropenidx, CT.TreeItemIcon_Expanded)
                for f in files:
                    if f.endswith('.py') or f.endswith('.bgp') or f.endswith('.tmpl'):
                        if root=='plugins' and f in ("__init__.py","Default.py"):
                            continue
                        treeItem=self.dirs.AppendItem(nodes[root], f, ct_type=CT.TREE_ITEMTYPE_CHECK)
                        self.dirs.SetPyData(treeItem,os.path.join(root,f))
                        if f.endswith('.py'):
                            s=self.Parent.il.scriptidx
                        elif f.endswith('.tmpl'):
                            s=self.Parent.il.templidx
                        elif f.endswith('.bgp'):
                            s=self.Parent.il.packageidx
                        self.dirs.SetItemImage(treeItem, s, CT.TreeItemIcon_Normal)
                        
                        
                        
            self.dirs.Expand(self.dirs.GetRootItem())
                