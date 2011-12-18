import wx
import wx.dataview as dv
from config import DEBUG
from properties import strbool
from os.path import join
from collections import OrderedDict


import random

columns=[
        "Name",
        u'Qt',
        u'Path',
        u'Fit',
        u'Dual',
        u'Rotated',
        u'Template',
#        'Values'
]


coltypes={
    'Name':'string',
    'Qt':'int',
    'Path':'string',
    'Fit':'bool',
    'Dual':'bool',
    'Rotated':'bool',
    'Template':'string'
}

defaults={
    "Name":"cardName",
    'Qt':1,
    'Path': join('img','ImgChoose.png'),
    'Fit':True,
    'Dual':False,
    'Rotated':False,
    'Template':None,
    'Values':dict()
}
    
columns_type={
              'Qt':int,
              'Dual ?': strbool,
              'Rotated ?': strbool,
              'Fit ?': strbool,
              }
     
template_columns_type={ 
    "str":dv.DataViewTextRenderer,
    "int":dv.DataViewTextRenderer,
    "float":dv.DataViewTextRenderer,
    "slider":dv.DataViewProgressRenderer,
    "bool":dv.DataViewToggleRenderer,
    "dir":dv.DataViewTextRenderer,
    "file":dv.DataViewTextRenderer,
    "date":dv.DataViewTextRenderer,
    "font":dv.DataViewTextRenderer,
    "color":dv.DataViewTextRenderer,
    "img":dv.DataViewTextRenderer, 
    'list':dv.DataViewTextRenderer,
    'imglist':dv.DataViewTextRenderer,
    'mchoices':dv.DataViewTextRenderer,
    'choice':dv.DataViewTextRenderer,
    'new_choice':dv.DataViewTextRenderer,    
}
     
class DeckCard(object):
    def __init__(self,Name="",Qt=1,Path="",Fit=True,Dual=False,Rotated=False,Template=None,Values=None):
        self.Name=Name
        self.Qt=Qt
        self.Path=Path
        self.Fit=Fit
        self.Dual=Dual
        self.Rotated=Rotated
        self.Template=Template
        if Values==None:
            Values=dict()
        self.Values=Values
        
    def __repr__(self):
        return 'DeckCard: %d of %s (with template %s)'%(self.Qt,self.Path,self.Template)
     
class DeckModel(dv.PyDataViewIndexListModel):
    def __init__(self):
        dv.PyDataViewIndexListModel.__init__(self)
        self.templateColumns=OrderedDict()
        self.cards=list()

    def GetColumnCount(self):
        return len(columns)+len(self.templateColumns)
                 
    def GetColumnType(self,col):
        if col<len(columns):
            return coltypes[columns[col]]
        else:
            return self.templateColumns[col-len(columns)]
        
    def DeleteRows(self, rows):
        # make a copy since we'll be sorting(mutating) the list
        rows = list(rows)
        # use reverse order so the indexes don't change as we remove items
        rows.sort(reverse=True)
        for row in rows:
            # remove it from our data structure
            del self.cards[row]
            # notify the view(s) using this model that it has been removed
        self.RowsDeleted(rows)
            
    def AddRow(self, value):
        # update data structure
        self.cards.append(value)
        # notify views
        self.RowAppended()
        
    # Report the number of rows in the model
    def GetCount(self):
        return len(self.cards)
        
    def GetChildren(self,parent,children):
        print 'getchildren',parent,children
        if not parent:
            for card in self.cards:
                children.append(self.ObjectToItem(card))
            return len(self.cards)
        return 0
    
    def IsContainer(self,item):
        return False

    def GetValue(self,row,col):
        card=self.cards[row]
        if col<len(columns):
            return getattr(card,columns[col])
        v=card.Values.get(self.templateColumns.keys()[col-len(self.view.cols) -1],None)
        if type(v)==type(wx.Colour()):
            v='rgba'+str(v)
        return v
        
    def GetValueByRow(self,row,col):
        return self.GetValue(row,col)
        
    #getattr
    def GetParent(self,item):
        # Return the item which is this item's parent.
        return dv.NullDataViewItem
    
    def SetValue(self,value,row,col):
        card=self.cards[row]
        if col<=len(columns)-1:
            setattr(card,columns[col],value)
        else:
            card.values[self.templateColumns.keys()[col-len(columns)]]=value
        self.RowChanged(row)
    
class DeckGrid(dv.DataViewCtrl):
    def __init__(self, parent):
        # Create a dataview control
        dv.DataViewCtrl.__init__(self,parent,
                                   style=wx.BORDER_THEME
                                   | dv.DV_ROW_LINES # nice alternating bg colors
                                   #| dv.DV_HORIZ_RULES
                                   | dv.DV_VERT_RULES
                                   | dv.DV_MULTIPLE
        )
        self.parent=parent
        self.model=DeckModel()
        self.model.view=self
        self.AssociateModel(self.model)
        self.AppendTextColumn("Name", 0,width=80)
        self.AppendTextColumn("Qt",   1,width=30, align=wx.ALIGN_CENTER,mode=dv.DATAVIEW_CELL_EDITABLE)
        self.AppendTextColumn("Path",  2, width=100, align=wx.ALIGN_CENTER)
        #self.AppendToggleColumn("Fit",  3, width=50, align=wx.ALIGN_CENTER,mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        self.AppendToggleColumn("Dual", 4, width=50, align=wx.ALIGN_CENTER,mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        self.AppendToggleColumn("Rotated",5,  width=60,  align=wx.ALIGN_CENTER,mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        self.AppendTextColumn("Template",  6, width=60)

        # Through the magic of Python we can also access the columns
        # as a list via the Columns property.  Here we'll mark them
        # all as sortable and reorderable.
        for c in self.Columns:
            c.Sortable = True
            c.Reorderable = True

        # Bind some events so we can see what the DVC sends us
        self.Bind(dv.EVT_DATAVIEW_ITEM_EDITING_DONE, self.OnEditingDone, self)
        self.Bind(dv.EVT_DATAVIEW_SELECTION_CHANGED,self.OnSelectionChanged)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyDown)
        self.Bind(wx.EVT_CHAR, self.OnKeyDown)
        self.Bind(dv.EVT_DATAVIEW_ITEM_VALUE_CHANGED,self.OnValueChanged)
        
        self.sel=None
        self.cols=['Name','Qt','Path','Dual','Rotated','Template']
        
    def OnValueChanged(self,event):
        self.OnSelectionChanged(event,force=True)
        
    def OnSelectionChanged(self,event,force=False):
        items=self.GetSelections()
        rows=[self.ItemtoRow(row) for row in items if row.IsOk()]
        numcol=len(columns)
        if not rows:          
            return
        row=rows[-1]
        dc=self.model.cards[row]
        if self.sel==dc and not force:
            return
        else:
            self.sel=dc
        self.RefreshView(dc)
        
    def RefreshView(self,dc):
        self.parent.rotated.Value= dc.Rotated
        self.parent.dual.Value= dc.Dual
        #int is there to adressa shortcoming of DVC view.
        self.parent.spin.Value=dc.Qt
        #Here, we force the template
        self.parent.SetCard(dc.Path,template=dc.Template, values=dc.Values)
        #Also update the propgrid
        if dc.Template:
            try:
                self.parent.propgrid.Build(self.parent.templates[dc.Template])
                if dc.Values:
                    self.parent.propgrid.UpdateValues(dc.Template,dc.Values)
            except KeyError:
                self.parent.Warn("Template Name '%s' not Found"%dc.Template)      
        
    def RefreshColumns(self):
        colsLabels={x.Title for x in self.Columns}
        cs={x.Title:x  for x in self.Columns}
        ts=dict()
        tlabels=set()
        for card in self.model.cards:
            for k in card.Values:
                t=self.parent.templates[card.Template]
                if k in t.column:
                    tlabels.add(k)
                    ts[k]=card.Template
        for c in columns:
            tlabels.add(c)
        toaddlabels=tlabels-colsLabels-set(columns)
        tosupprlabels=colsLabels-tlabels
        for l in toaddlabels:

            typ,default=self.parent.templates[ts[l]].column[l]
            tr = template_columns_type[typ](mode=dv.DATAVIEW_CELL_ACTIVATABLE)

            col = dv.DataViewColumn(l,   # title
                                   tr,        # renderer
                                   len(self.cols)+len(self.model.templateColumns)+1,         # data model column
                                   width=80
                                   )
            self.AppendColumn(col)
            
            #col=self.AppendTextColumn(l,len(self.cols)+len(self.model.templateColumns)+1)
            self.model.templateColumns[l]=col
        #issue with the templtecaolums: removing column would be too hard=> return from herre
        return
        for l in tosupprlabels:
            self.DeleteColumn(cs[l])
            del self.model.templateColumns[l]
            
    def OnKeyDown(self, event):
        event.Skip()
        if event.GetKeyCode()==wx.WXK_DELETE:#supr line
                    self.DeleteSelections()

    def GetValue(self,row,col):
        return self.model.GetValue(row,col)
        
    def SetValue(self,value,row,col):
        self.model.SetValue(value, row, col)
        
    def DeleteSelections(self):      
        items = self.GetSelections()
        rows=[self.ItemtoRow(item) for item in items if item.IsOk()]
        rows.sort(reverse=True)
        self.model.DeleteRows(rows)
        self.parent.updateinfo()
        self.RefreshColumns()
        
    def AppendRow(self, row):
        card=DeckCard(*row)
        self.AppendCard(card)
        
        
    def AppendCard(self,card):
        self.model.AddRow(card)
        #check if column are missing
        self.RefreshColumns()
        
    def GetSelectedCard(self):
        s=self.GetSelection()
        if s.IsOk():
            return self.model.cards[self.ItemtoRow(s)]
        return DeckCard(*[None]*8)

    def MultiUpdate(self,newCard,_cfilter,_tfilter):           
        #For all items, update the value to data ones, except for the pictures & name
        items=self.GetSelections()
        for item in items:
            if not item.IsOk(): continue
            rowNum=self.ItemtoRow(item)
            card=self.model.cards[rowNum]
            for colName in _cfilter:
                setattr(card,colName,getattr(newCard,colName))
            for colName in _tfilter:
                card.Values[colName]=newCard.Values[colName]
            self.model.RowChanged(rowNum)
        self.RefreshColumns()

    def GetData(self):
        res=list()
        for i in range(len(self.model.cards)):
            line=list()
            for j in range(len(self.Columns)):
                line.append(self.model.GetValue(i,j))
            res.append(line)
        return res
        
    def GetDeckSize(self,dual=False):  
        front,back=0,0
        for i in range(len(self.model.cards)):
            #Int has been added to address a shortcoming in MVC datavaiew widget
            dc=self.model.cards[i]            
            if dc.Dual:
                back+=dc.Qt
            else:
                front+=dc.Qt     
        if dual:
            return (front,back)
        return front+back
    
    def ItemtoRow(self,item):
        return self.model.GetRow(item)

    def OnEditingDone(self, evt):
        print 'editing dine'
        item=evt.GetItem()
        row=self.ItemtoRow(item)
        dvc=evt.DataViewColumn
        iso=lambda x:x
        _xfo=columns_type.get(dvc.Title,iso)
        col=columns.index(dvc.Title)
        oldval=self.GetValue(row, col)
        self.SetValue(_xfo(oldval),row,col)

    def Save(self,path,fitting_size):
        import csv
        from csv import writer
        from os.path import split
        import os
        #from yaml import dump
        filename=split(path)[-1]
        spamWriter = writer(file(path, 'wb'), delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamWriter.writerow(['Fitting Size',str(fitting_size)])
        #Gather all possible labels
        labels=columns[:]
        for line in range(len(self.model.cards)):
            #Get the values
            vs=self.GetValue(line,len(columns)-1)
            for k in vs:
                if k not in labels:
                    labels.append(k)
        spamWriter.writerow(labels)
        for i in range(len(self.model.cards)):
            line=[None]*len(labels)
            for j in range(len(columns)-1):#-1 because not doing the values
                line[j]=self.GetValue(i,j)
            vs=self.GetValue(i,len(columns)-1)
            for k in vs:
                cindex=labels.index(k)
                #iF NECESSARY? CONVERT TO UNICODE
                ##New yaml stuff
                ##_tmp=dump(vs[k]).split('\n')[0].strip()
                _tmp=unicode(vs[k]).encode('cp1252').split('\n')[0].strip()
                line[cindex]=_tmp
                #~ if getattr(vs[k],'decode',None):
                    #~ line[cindex]=vs[k].encode('cp1252')
                #~ else:
                    #~ line[cindex]=vs[k]
            spamWriter.writerow(line)
        #New deck style: insert the fiiting sie at the start of the deck
        self.parent.statusBar1.SetStatusText('Deck Saved !')
        self.parent.SetTitle(filename)
        self.parent.deckdir,self.parent.deckname=os.path.split(filename)

    def Load(self,path,appendMode=False):
        import csv
        #from unicode_csv import UnicodeReader as reader
        print 'skipping univcode csv for now'
        from csv import DictReader, reader
        if not appendMode:
            self.SelectAll()
            self.DeleteSelections()
        spamReader=reader(file(path,'rb'), delimiter=';')
        iso=lambda x:x
        getters=[]
        for i,row in enumerate(spamReader):
            if DEBUG:
                print '*'*60
                print i, len(row), row
            if i<2:
                if i==0:
                    #Fitting Size
                    try:
                        fitting_size=[int(x) for x in row[1].strip()[1:-1].split(',')]
                        self.parent.fitting_size=fitting_size
                    except ValueError:
                        print '[Warn] Fitting Size line not corrent in CSV Deck File',row                        
                        pass
                    continue
                if i==1:
                    #Labels
                    labels=row
                    #Now, for non existing row, add a fake value
                    for label in columns:
                        if label in labels:#return a getter of the proper column, applying the load XFO                        
                            getters.append(lambda _row:columns_type.get(label,iso)(_row[labels.index(label)]))
                        else:                          
                            getters.append(lambda _row:defaults[label])
                    break
        csvsrc=file(path,'rb')
        csvsrc.next()#first line removed
        csvsrc.next()#second line removed
        dictReader=DictReader(csvsrc,fieldnames=labels,delimiter=';',)
        for i, row in enumerate(dictReader):
            card=DeckCard()
            ##grow=[]
            for l in columns:
                if l in row:
                    ##grow.append(columns_type.get(l,iso)(row[l]))
                    setattr(card,l,columns_type.get(l,iso)(row[l]))
                else:
                    ##grow.append(defaults[l])
                    setattr(card,l,defaults[l])
            #print grow

            templateName=row.get('Template','')
            templateName=card.Template
            if templateName:
                _vs=row.copy()
                for l in columns:
                    if l in _vs:
                        del _vs[l]
                
                #Ensure template is present in current libray:
                if templateName not in self.parent.templates:
                    self.parent.LoadTemplate(templateName)
                    
                #in place xfo
                #~ print "row empty:",grow[-1]
                #print "vs before",_vs
                _vs=self.parent.templates[templateName].UnSerializeValues(_vs)
                card.Values=_vs
                ##grow[-1]=_vs
                #print "vs after",_vs                
                #grow[-1]={'width':2,"extension":True,"radius":3,"offset":1,"color_out":"white","color_in":"green"}
                #if DEBUG: print 'Adding to deck row',grow
                if DEBUG: print 'Adding to deck card',card
            ##self.AppendRow(grow)
            self.AppendCard(card)

