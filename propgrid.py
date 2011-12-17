"BGM Propgrid options for template"
import wx
import wx.propgrid as wxpg
from properties import forms, properties, editors, SliderPropertyEditor, strcolor
from config import DEBUG

class ValueObject:
    def __init__(self):
        pass

def  UnSerialize(data):
        import datetime
        sandbox = {
                'obj':ValueObject(),
                'wx':wx,
                'datetime':datetime}
        if data:
            exec data in sandbox
        return sandbox['obj'].__dict__

class CustomPropertyGrid(wxpg.PropertyGridManager):
    def __init__(self,parent):
        wxpg.PropertyGridManager.__init__(self,parent,
                                          style=
                                            wxpg.PG_SPLITTER_AUTO_CENTER |
                                            #wxpg.PG_AUTO_SORT |
                                            wxpg.PG_TOOLBAR
                                        )
        self.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)

        self.Bind( wxpg.EVT_PG_CHANGED, self.OnPropGridChange )
        self.RegisterEditor(SliderPropertyEditor)
        self._pages=dict()
        
    def ClearAllPage(self):
        for i in range(self.GetPageCount()):
            self.RemovePage(0)

    def SerializeValues(self,template,additional_values=None):
        if template not in self._pages:
            print '[WARN]: should not be possible to update without creating first. Template never created'
            return ""
        page=self.GetPage(template)
        d = page.GetPropertyValues(inc_attributes=True)
        ss = []
        if additional_values is not None:
            d.update(additional_values)
        for k,v in d.iteritems():
            v = repr(v)
            if not v or v[0] != '<':
                if k.startswith('@'):
                    ss.append('setattr(obj, "%s", %s)'%(k,v))
                else:
                    ss.append('obj.%s = %s'%(k,v))
        return str(ss)
    
    def UnSerializeValues(self,value_strings):
        return UnSerialize(value_strings)
        
    def UpdateValues(self,templateName,values):
        if templateName not in self._pages:
            print '[WARN]: should not be possible to update without creating first. Template never created'
            return
        page=self.GetPage(templateName)
        d=self.GetPropertyValues()
        template=self.Parent.templates.get(templateName)   
        for name in values:
            p=page.GetPropertyByName(name)
            if p:
                p.SetValue(values[name])
        
    def OnPropGridChange(self,event):
            event.Skip()
            self.Parent.SetCard()
            
    def Build(self,template):
        EXISTING=False
        #Get Current Template info
        if template.name in self._pages:
            self.SelectPage(template.name)
            page=self.GetCurrentPage()
            EXISTING=True
        else:
            self._pages[template.name]=template
            page=self.AddPage( template.name)
            page.Append( wxpg.PropertyCategory("%s - %s"%(template.name,template.help)))
        for colname in template.column:
            OLDVALUE=False
            #If replacing an exiting grid, first remove the property if it exists
            if EXISTING:
                p=page.GetPropertyByName(colname)
                if p: 
                    oldpropertyvalue=p.GetValue()
                    OLDVALUE=True
                    page.DeleteProperty(p)
            #print colname, template.column[colname]
            _typ,val=template.column[colname]
            if _typ=="color":
                if type('')==type(val):
                    val=strcolor(val)
            else:
                if val is None:
                    val=""
            #print _typ, colname,val
            #print forms[_typ](colname,value=val)
            ##In case of choice, create a list of choices for the choices           
            if _typ in ("choice",'new_choice'):
                init,vals=val,template.choices[colname]
                try:
                    value=vals.index(init)
                except ValueError:
                    value=0
                _prop=page.Append(forms[_typ](colname,value=vals[value]))
                _prop.SetPyChoices(vals)
            else:
                _prop=page.Append( forms[_typ](colname,value=val))
            _data=properties.get(_typ,())
            if  _data:
                for pgprop in _data:
                    page.SetPropertyAttribute(colname, *pgprop)
            #Special hack for int type spin
            _data=editors.get(_typ,())
            if _data:
                page.SetPropertyEditor(colname,_data)
            #now, when replacing eisting properyt, reset oldvalues if it existed
            if OLDVALUE:
                _prop.SetValue(oldpropertyvalue)
        self.SelectPage(template.name)

