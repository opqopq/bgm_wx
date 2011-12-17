"Define template & script objects"
import wx.propgrid as wxpg
import wx
import  wx.lib.filebrowsebutton as filebrowse
import wx.lib.scrolledpanel as scrolled
from collections import OrderedDict
import config
from config import print_size as fitting_size

from collections import OrderedDict
class Template:
    "Template File. To be subclassed. Only the process method should be define & overiden"	
    name=""
    help=""
    column=OrderedDict()
    isTemplate=False
    fitting_size=None
    dir=None
        
    def process(self,dc,values):
        raise NotImplementedError('process method from abstract class Template')
        
    def draw(self,imagePath,fit_size,values):
        #Return a PIL object with the image to be draw
        import wx,os.path
        if not os.path.isfile(imagePath):
            img=wx.EmptyImage(*fit_size)
        else:
            img=wx.Image(imagePath)
            img=img.Rescale(*fit_size)
        img=self.format(img,values)
        return self.imageToPil(img)
    
    def format(self,wximage,values):
        "Return a wx.Image object with the image to be displayed"
        #Create a value dict from the default ones, updated with the selected one
        _v=self.GetValues()
        if values:
            for val in values:
                if val not in _v:continue
                _v[val]=values[val]   
        import wx
        #First rescale the given image to comply to ftting size
        if self.fitting_size:
            wximage.Rescale(*self.fitting_size)
        bitmap=wx.BitmapFromImage(wximage)
        dc = wx.MemoryDC()
        dc= wx.BufferedDC(dc)
        dc.SelectObject(bitmap)
        try:
            # draw on the dc using any of the Draw methodst
            bmp=self.process(dc,_v)
            #Done
        finally:
            dc.SelectObject(wx.NullBitmap)
            dc.SetPen( wx.NullPen )
            dc.SetBrush( wx.NullBrush )            
        # the bitmap now contains wahtever was drawn upon it
        del dc
        if bmp:
            #~ if self.fitting_size:#template file=> they have their own fitting size
                #~ return wx.ImageFromBitmap(bmp).Rescale(*self.fitting_size)
            return wx.ImageFromBitmap(bmp)
        if self.fitting_size:
            return wx.ImageFromBitmap(bitmap).Rescale(*self.fitting_size)
        return wx.ImageFromBitmap(bitmap)

    def GetValues(self):
        res=dict()
        for key in self.column:
            res[key]=self.column[key][1]
        return res
        
    def imageToPil(self,image):
        import Image
        pil = Image.new('RGB', (image.GetWidth(), image.GetHeight()))
        pil.fromstring(image.GetData())
        return pil
        
    def UnSerializeValues(self,value_dict):
        "Take a values dict from a saved CSV file a recreate the dict with the good types"     
        from properties import xfos,iso      
        for col in self.column:
            ##print 'chaging the skip method used for unkown values',
            if col not in value_dict: continue
            _typ,_default=self.column[col]
            val=value_dict.get(col,_default)
            if val!=_default:
                val=xfos.get(_typ,iso)(val)
            value_dict[col]=val       
        return value_dict
        
class EmptyTemplate(Template):
    name="Empty"
    def draw(self,cardPath,fit_size,values):
        import Image, os.path
        if not os.path.isfile(cardPath):
            #"No image in here => rendering an empty one"
            #Render null image
            return Image.open('blank.png','r')
        return Image.open(cardPath,'r')
        
    def format(self,wximage,values):
        return  wximage

template_empty=EmptyTemplate()

def make_template(template_filename):
    import os.path, cPickle
    from properties import typematch
    from  widgets import FieldFromValues
    tdir,filename=os.path.split(template_filename)
    script=""
    #Helper Function
    def getorder(element):
        t,v=elts[element]
        order= v.get('z index',0)
        if order is None:
            order=0
        return order
    IsPackage=template_filename.endswith('.bgp')
    #convert to list. otherwise, it is a generator, which may not be re-used
    #Disinction between simple tmpl file=>pickle & .zip file=>load them
    if not IsPackage:
        elts=cPickle.load(file(template_filename,'rb'))
        filename_no_ext=os.path.splitext(filename)[0]
        #filename_no_ext='script'
        script_name=os.path.join(tdir,filename_no_ext+'.py')
        if os.path.isfile(script_name):
            script=file(script_name,'rb')
    else:
        from package import Package
        p=Package(template_filename)
        elts=cPickle.load(p.template)
        script=p.script
    #it is a dict mapping elt name with (type, values)
    a=Template()
    #Show that this is a real template and not just some code
    a.isTemplate=True
    #if filename is inside the card folder, replace by relative path
    if template_filename.startswith(config.card_folder):
        a.name=os.path.relpath(template_filename,start=config.card_folder)
    else:
        a.name=template_filename
    a.help='Template from file %s'%filename
    a.column=dict()
    a.dir=tdir
    a.widgets=OrderedDict()
    a.choices=dict()#create a dict to contains all choices list for a given elements
    for x in sorted(elts, key=lambda x:getorder(x)):
        Type,vs=elts[x]
        obj=FieldFromValues(Type,vs)
        a.widgets[obj.name]=obj
        #Now link the widget to the template, somehow
        obj._template=a
    #Now, create script columns for default actions view
    for name in elts:
        Type,values=elts[name]
        if Type.lower()=='template':
            #Create a fitting size based on template size - only if one is defined
            a.fitting_size=(values['card width'],values['card height'])
            continue
        #Only loop on printable elts. For each of these, let user choose the changeable parameter: text for text, image path for image, color for color, chocie for choice
        tp=typematch.get(Type.capitalize(),None)
        if tp is None:#Not a changeable element
            continue
        if tp=="choice":
            a.column[values['name']]="new_choice",values['default']
            a.choices[values['name']]=values['choices']
            continue
        #If field is NOT editable, just do not offer to edit it
        if values['editable']==False:
            continue
        a.column[values["name"]]=tp,values['default']
        #Give a link to element template
    skipped=('Set','Info','StaticImage')
    #Apply script on each widgets
    ##Exec script first
    if script:
        import new
        script_vars=dict()
        exec script.read()in script_vars
        ##Then bind it to widget
        for wName in a.widgets:
            w=a.widgets[wName]
            if 'on_%s_displaying'%w.name in script_vars:
                w.OnDisplaying=new.instancemethod(script_vars['on_%s_displaying'%w.name],w,w.__class__)
            if 'on_%s_displayed'%w.name in script_vars:
                w.OnDisplayed=new.instancemethod(script_vars['on_%s_displayed'%w.name],w,w.__class__)
            if 'on_%s_create'%w.name in script_vars:
                print 'useless: object is already created when link happens'
                w.OnCreate=new.instancemethod(script_vars['on_%s_create'%w.name],w,w.__class__)
                print w.name,'matched in creation'
            if 'on_%s_change'%w.name in script_vars:
                print 'useless: the only important change is the one in display with gridvalue...'
                w.OnChange=new.instancemethod(script_vars['on_%s_change'%w.name],w,w.__class__)                
                print w.name,'matched in change'
    def process(dc, values):
        for objName in a.widgets: #getattr and not Xx. to have Tempalte element not revert to a bug
            obj=a.widgets[objName]            
            #Type,vs=elts[elt]
            Type=obj.Type
            if Type=='template':
                #Fill the stuff with card background, it color & size
                #~ dc.SetBrush(wx.Brush(vs['card background'],wx.SOLID))
                #~ dc.DrawRectangle(0,0,*a.fitting_size)
                #~ dc.SetBrush( wx.NullBrush )            
                continue
            if Type in skipped:
                continue
            #Change elt values with propgrid values
            #Only loop on exportable parameter and not the onefixed in the template file
            #If case the element is not editable, there is not values[elt]=>just give empty string (none not working with Render)
            obj.Render(values.get(obj.name,""),dc,a,values)
    import new
    a.process=new.instancemethod(process,a,Template)
    a.process=process
    return a
    
class TemplateDirectory():
    def __init__(self):
        self._values=dict()
    
    def get(self,value,default=None):
        try:
            return self[value]
        except KeyError:
            return default
            
    def __contains__(self,item):
        return item in self._values
    
    def __getitem__(self,item):
        "Get a template & load if necessary from file"
        if item in self._values:
            return self._values[item]
        import os.path
        if os.path.isfile(item):
            if item.endswith('tmpl') or item.endswith('.bgp'):
                t=make_template(item)
                #do not cache this. just recompute them each time
                ##self._values[item]=t
                return t
            elif item.endswith('py'):
                #Load all template from file
                _vars=dict()
                execfile(item,globals(),_vars)
                num=0
                for name in _vars:
                    if name.startswith('template_'):
                        num+=1
                        t=_vars[name]
                        self._values[t.name]=t
                #Save the last loaded template of linked to the py file
                if num:
                    self._values[item]=t
                    return t
                else:
                    print ".Py file does not contains any template file"
        else:
            import os.path
            if os.path.abspath(item)!=item:
                try:
                    return self.__getitem__(os.path.abspath(item))
                except KeyError:
                    # 'not abspath'
                    pass
            #Try with a different path
            if os.path.join(config.card_folder,item)!=item:
                try:
                    return self.__getitem__(os.path.join(config.card_folder,item))
                except KeyError:
                    # 'not relpath either'
                    pass
        if not item:
            return None
        raise KeyError("Not a path or a template:"+item)
    
    def __setitem__(self,item,values):
        self._values[item]=values

class Script:
    name=""
    help=""
    column=dict()    
    isScript=True
    
    def run(self,mainframe,values):
        raise NotImplementedError("Run method")
        

        