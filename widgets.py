"Handle all operation on a template element"
import os, os.path
import wx
from collections import OrderedDict 
from config import MSE_VERSION, card_folder
from wx.lib.wordwrap import wordwrap


## Help for playing with image transparency
def SetAlpha(bmp,value):
    if value==255:
        return bmp
    Img=bmp.ConvertToImage()
    if not Img.HasAlpha():
        Img.InitAlpha()
    ad=Img.GetAlphaData()
    alphas_before=dict.fromkeys(ad)
    def trans(a):
        return ('%02x'%(int(a.encode('hex'),16)* value/255)).decode('hex')
    alphas_after={x:trans(x) for x in alphas_before}
    if len(alphas_before)==1:
        newad=len(ad)*alphas_after.values()[0]
    else:
        newad=''.join(alphas_after[a] for a in ad)
    Img.SetAlphaData(newad)
    return Img.ConvertToBitmap()
    
class Parameter:
    def __init__(self,typ,value,component='game'):
        self.typ=typ
        self.value=value
        self.component=component
        if typ in ('list','imglist') and not value:
            self.value=[]
        
    def copy(self):
        return Parameter(self.typ,self.value,self.component)
        
    def __repr__(self):
        return "<Paramter %s:%s>"%(self.typ,self.value)

    def fromText(self,value):
        _t=self.typ
        _v=value
        if _t=="str":
            if _v is None:
                _v=""
            _v=str(_v)
        elif _t in ('file','img'):
            if _v is None:
                _v=""
        elif _t=="int":
            if _v is None:
                _v=0
            try:
                _v=int(_v)
            except ValueError:
                print self ,'forced with a script?:',_v
                _v=0
        elif _t=="float":
            if _v is None:
                _v=0.0
            _v=float(_v)
        self.value=_v
        
    def export(self,typ):
        import os.path
        _t,v=self.typ,self.value
        #Keep this one. ensure template stay clean of added values
        ##Special Case
        if _t=="bool":#Convert False & True to mse value
            v=str(v).lower()
        elif _t in ('file','img'):#in case of file, just take the filename
            v=os.path.split(v)[-1]
        elif _t =="mchoices":
            v=" ".join(v)
        elif _t == "choice":
            #wx bug: sometime, v is the value. other, the index
            if type(v)==type(1):
                #V is only the index. find the string
                from MSE import ENUMS
                v=ENUMS[s][v]
        elif _t=="font":
            _thefont=FontTemplate()
            _thefont.fromObj(v)# v is the property with font data....
            v=_thefont.export()
        elif  _t=='color':
            v='rgba(%d,%d,%d,%d)'%(v.Red(),v.Green(),v.Blue(),v.Alpha())
        ##End special cases
        return v
        
##Base Class for Export and reading a propertygrid
class Element(object):
    name=""
    template=''
    end=''
    additional_param_template="\t%s: %s"
    specific_params=list()
    
    def __repr__(self):
        return "<Widget %s:%s>"%(self.__class__.__name__,self['name'])

    def __init__(self):
        self.params=OrderedDict()
        import inspect
        for klass in reversed(inspect.getmro(self.__class__)):
            if klass==object:
                continue
            for k,v in klass.specific_params:
                self.params[k]=Parameter(*v)
        #Script Hook
        self.OnCreate()
        
    def get(self,item,default=None):     
        try:
            return self[item]
        except AttributeError:
            return default
        
    def __getitem__(self,item):
        if item in self.params:
            return self.params[item].value
        return getattr(self,item)
        
    def __setitem__(self,item,value):
        #On Change Hook
        try:
            old_value=self[item]
        except AttributeError:
            #value does not exist yet....
            old_value=None
        self.OnChange(item,old_value,value)
        if item in self.params:
            self.params[item].value=value
            return
        return setattr(self,item,value)
        
    def export(self,typ='game'):
        if typ=='style':
            end=getattr(self,'end_style',self.end)
        elts=[]
        elts.append(self.template%self)
        for s in self.params:
            if self.params.component!=typ:
                continue
            if self.params[s].value is None:
                continue
            v=self.params[s].export(typ)
            elts.append(self.additional_param_template%(s,v))
        #only add a trailing line if needed
        if end:
            elts.append(end)
        return os.linesep.join(elts)
        
    def fromObj(self,obj):
        _vs=obj.GetValues()
        self.fromValues(_vs)
        
    def fromValues(self,_vs):
        for v in self.params:
            try:
                val=_vs[v]
            except KeyError:
                print "Warning: provided template does not support following params:%s"%v
                print 'Setting it to default value:',self.params[v].value
                val=self.params[v].value
            elt=self
            self.params[v].value=val
            ##some hacling in here. what will this change ???
            if self.params[v].typ=='font':
                subvs={x:_vs[x] for x in _vs if x.startswith('font.')}
                for x in subvs:
                    self[x]=subvs[x]
        
    def fromText(self,line):
        if line.strip().startswith('#'):
            return
        if not line.strip():
            return
        name,v=line.strip().split(':',1)
        name=name.strip()
        v=v.strip()
        if name in self.params:
            self.params[name].fromText(v)
        elif name=="type":
            self.Type=v
        elif name=="choice" and self.Type in ("choice","color"):
            self.params['choices'].value.append(v)
        elif name=='right':
            self.params['left'].fromText(self.params['width']-int(v))
        elif name=='bottom':
            self.params['top'].fromText(self.params['height']-int(v))
        else:
            print "While importing line %s"%line.strip(),self,'did not found parameter:',name
            
    def toProp(self):
        pass
        
    def toStyleText(self):
        return self.export(typ='style')
        
    def toGameText(self):
        return self.export(typ='game')
        
    def Draw(self,dc,gridvalue,template):
        print 'Drawing',self.Type,gridvalue
        
    def Render(self,gridvalue,dc,template,_values,isPaint=False):
        print 'Rendering ',self.Type,gridvalue,template,_values,isPaint
        
    def OnDisplaying(self,memDC,widgetValue,gridValues):
        pass
    
    def OnDisplayed(self,memDC,widgetValue,gridValues):
        pass

    def OnCreate(self):
        pass
    
    def OnChange(self,itemName,oldvalue,newvalue):
        pass

class FontTemplate(Element):
    additional_param_template="\t\t\t%s: %s"
    specific_params=[
        ('name',['str','Tahoma']),
        ('size',['int',72]),
        ('scale down to',['int',8]),
        ('max strech',['float',None]),
        ('weight',['str',None]),
        ('style',['str',None]),
        ('underline',['bool',False]),
        ('color',['color',wx.Colour()]),
        ('shadow color',['color',None]),#default to transparent
        ('shadow displacement x',['float',None]),
        ('shadow displacement y',['float',None]),
        ('shadow blur',['float',None]),
        ('separate color',['color',None]),
        ('Family',['str',None]),
    ]
    def fromObj(self,obj):
        for n in self.specific_params:
            _n,_items=n
            value=obj.GetPropertyByName(_n).GetValue()
            self.params[_n].value=value
        #Remove the family only used by wx and not MSE
        self.params['Family']=Parameter('str',None)
        
    def fromValues(self,_vs):
        for _n,_items in self.specific_params:
            value=_vs['font.'+_n]
            self.params[_n].value=value
        
class SetTemplate(Element):
    Type='set'
    additional_param_template="%s: %s"
    specific_params=[
        ('name',['str',None]),
        #('game',['str',None]),
        ('excel cards file',['file',None]),
    ]
    template="""mse version: %s
"""%MSE_VERSION

    def fromObj(self,obj):
        Element.fromObj(self,obj)
        self.game_name=obj.game_name
        self.style_name=obj.style_name
        #Remove link to excel card file 
        self.params['excel cards file']=Parameter('file',None)
        self.params['name']=Parameter('str',None)
        
    def export(self):
        return os.linesep.join([Element.export(self),"game: %s"%self.game_name,"stylesheet: %s"%self.style_name])
        
class GameTemplate(Element):
    Type="template"
    name="Template"
    additional_param_template="%s: %s"
    specific_params=[
        ('short name',['str','theName']),
        ('full name',['str','theFullname']),
        ('position hint',['int',670]),
        ('icon',['img',None]),
        ('version',['str',"1.0"]),
        ('style short name',['str','Style','style']),
        ('style full name',['str','My Game Style','style']),
        ('style icon',['img',None,'style']),
        ('style position hint',['int',None,'style']),
        ('card background',['color',wx.NamedColour("white"),'style']),
        ('card width',['int',325,'style']),
        ('card height',['int',550,'style']),
        ('card dpi',['int',150,'style']),
        ('init script',['str',None,'style']),
        ('mse version',['str',MSE_VERSION]),
        ('mse version',['str',MSE_VERSION,'style']),
        ('depends on',['list',None]),
        ('depends on',['list',None,'style']),
    ]
    template="""#Create with OPQ's MSE DESIGNER
mse version: %s
"""%MSE_VERSION
    end_style="""#include
card style:"""

    #Re-implementing form obej for game, depends on
    def fromObj(self,obj):
        Element.fromObj(self,obj)
        _vs=obj.GetValues()
        self.params['depends on']=Paramter('str','%s.mse-game %s'%(_vs['short name'],_vs['version']),'style')

    def Render(self,gridvalue,dc,template,_values,isPaint=False):
        w,h=self['card width'],self['card height']
        pen=wx.Pen('red')
        brush=wx.Brush('white')
        dc.SetPen(pen)
        dc.SetBrush(brush)
        dc.DrawRectangle(0,0,w,h)
        dc.DrawText("Template--",w/2,h/2)#take care of text extent at some point

        
##Base Class for all field in a game file
class GameField(Element):
    Type='theType'
    specific_params=[
        ('name',['str',None]),
        ('description',['str',None]),
        ('identifying',['bool',None]),
        ('editable',['bool',None]),
        ('save value',['bool',None]),
        ('show statistics',['bool',None]),
        ('card list allow',['bool',None]),
        ('card list alignment',['mchoices',None]),
        ('card list column',['int',None]),
        ('card list name',['str',None]),
        ('card list width',['int',None]),
        ('card list visible',['bool',None]),
        ('card list visible',['str',None]),
        ('icon',['file',None]),
        ('top',['int',0,'style']),
        ('left',['int',0,'style']),
        ('width',['int',0,'style']),
        ('height',['int',0,'style']),
        ('z index',['int',None,'style']),
        ('angle',['int',None,'style']),
        ('visible',['bool',None,'style']),
        ('mask',['img',None,'style']),
        ('alpha',['int',None]),
        
    ]
    template_game="""card field:
\ttype: %(Type)s"""

    additional_param_template="\t\t%s: %s"
    template_style="""
\t%(name)s:"""

    #Re-implementing fromObj 'cause of name issue
    def fromObj(self,obj):
        self.name=obj.GetValues()['name']
        Element.fromObj(self,obj)
        
    def Render(self,gridvalue,dc,template,_values,isPaint=False):
        #Display hook for Script
        self.OnDisplaying(dc,gridvalue,_values)
        #First create a contexttual memory DC with a memory bitmap to store the object to be drawned. At the end, blit it to dc
        #Find a mask color for drawing
        ##Warning: color is based on current DC, not on element color chossen; This may lead to issue while painting
        _bmp=wx.EmptyBitmap(self['width'],self['height'])
        oldDC=dc
        memDC=wx.MemoryDC(_bmp)
        if not isPaint:
            r,g,b=dc.GetAsBitmap().ConvertToImage().GetOrFindMaskColour()
            #Ensure alpha settings also
            mcolor=wx.Colour(r,g,b)
            memDC.SetBackground(wx.Brush(mcolor))
        memDC.Clear() 
        dc = memDC
        self.Draw(dc,gridvalue,template)
        memDC.SelectObject(wx.NullBitmap)
        #Handle masking
        if self['mask']:
            if os.path.isfile(self['mask']):
                if not isPaint:
                    _bmp.SetMaskColour(mcolor)
                BMP=wx.Bitmap(self['mask'])
                _bmp.SetMask(wx.Mask(BMP))                
            else:
                print 'Warning: mask not found (%s)'%self['mask']
        else:
            #Done with the draw
            if not isPaint:
                _bmp.SetMaskColour(mcolor)
        #Handle Alpha LAyer
        alpha=self['alpha']
        if alpha is not None:
            alpha=int(alpha)
            _bmp=SetAlpha(_bmp,alpha)
        #Handle rotation
        angle=self['angle']
        if not angle:
            angle=0   
        if angle:
            from math import radians
            img=_bmp.ConvertToImage()
            if not img.HasAlpha():
                img.InitAlpha()
            img=img.Rotate(radians(angle),wx.Point(img.Width/2,img.Height/2))
            _bmp=wx.BitmapFromImage(img)
        #Now blit and free stuff   
        oldDC.DrawBitmap(_bmp,self['left'],self['top'],True)
        #End of display hook
        self.OnDisplayed(dc,gridvalue,_values)


class InfoElement(GameField):
    Type="info"
    specific_params=[
        ("script",['str',None]),
        ("font",['font',wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT),'style']),
        ("alignment",['mchoices',None,'style']),
        ('padding left',['float',None,'style']),
        ('padding right',['float',None,'style']),
        ('padding top',['float',None,'style']),
        ('padding bottom',['float',None,'style']),
        ('background color',['color',wx.NamedColour('white'),'style']),
    ]
    
class KeywordElement(GameField):
    Type="keyword"
    specific_params=[
        ('keyword',['str',None]),
        ('match',['str',None]),
        ('reminder',['str',None]),
        ('rules',['str',None]),
        ('mode',['str',None]),        
    ]
  
class WordList(GameField):
    Type='wordlist'
    specific_params=[
        ('name',['str',None]),
        ('word',['list',None])
        
    ]
    
class ColorElement(GameField):
    Type='color'
    
    specific_params=[
        ('initial',['color',None]),
        ('default name',['str',None]),
        ('default',['color',None]),
        ('allow custom',['bool',None]),
        ('script',['str',None]),
        ('radius',['float',0,'style']),
        ('left width',['float',None,'style']),
        ('right width',['float',None,'style']),
        ('top width',['float',None,'style']),
        ('bottom width',['float',None,'style']),
        ('combine',['choice',None,'style']),        
        ('choices',['list',None,'style']),
    ]
    
    def Draw(self,dc,gridvalue,template):
        color= gridvalue or self['default']
        bw=self['bottom width']
        lw=self['left width']
        rw=self['right width']
        tw=self['top width']
        if bw and  lw and  rw and tw:
            #only the border
            width=min(bw,lw,rw,tw)
            pen=wx.Pen(color,width,wx.SOLID)
            brush=wx.Brush(color,wx.TRANSPARENT)
        else:
            #complete fill
            pen=wx.NullPen
            brush=wx.Brush(color,wx.SOLID)
        dc.SetPen(pen)
        dc.SetBrush(brush)
        dc.DrawRoundedRectangle(0,0,self['width'],self['height'],self['radius'])
        dc.SetPen(wx.NullPen)
        dc.SetBrush(wx.NullBrush)
     
class TxtElement(GameField):
    Type="text"

    specific_params=[
        ('default',['str',None]),
        ('multi line',['bool',None]),
        ('script',['str',None]),
        ("font",['font',wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT),'style']),
        ("alignment",['mchoices',None,'style']),
        ('always symbol',['bool',None,'style']),
        ('allow formating',['bool',None,'style']),
        ('direction',['mchoices',None,'style']),
        ('padding left',['float',None,'style']),
        ('padding left min',['float',None,'style']),
        ('padding right',['float',None,'style']),
        ('padding right min',['float',None,'style']),
        ('padding top',['float',None,'style']),
        ('padding top min',['float',None,'style']),
        ('padding bottom',['float',None,'style']),
        ('padding bottom min',['float',None,'style']),
        ('line height soft',['float',None,'style']),
        #('line height soft max',['float',1.0]),
        ('line height hard',['float',None,'style']),
        #('line height hard max',['float',1.0]),
        ('line height line',['float',None,'style']),
        #('line height line max',['float',1.0]),
        ('paragraph height',['int',None,'style']),
    ]
    
    def Draw(self,dc,gridvalue,template):
        #First handle the font
        left,top=self['left'],self['top']
        Weight=getattr(wx,'FONTWEIGHT_'+self['font.weight'].upper())
        Style=getattr(wx,'FONTSTYLE_'+self['font.style'].upper())
        Family=getattr(wx,'FONTFAMILY_'+self.get('font.Family').upper())
        font= wx.Font(self['font.size'], Family, Style, Weight, self['font.underline'], self['font.name'])
        pos=wx.Point(self['left'],self['top'])
        dc.Font=font
        dc.TextBackground='BLACK'#vs['font.color']
        dc.TextForeground=self['font.color']
        if gridvalue is None:
            gridvalue=self['default']
        if type(gridvalue) not in (type(""),type(unicode())):
            gridvalue=str(gridvalue)
        if self['editable']==False:
            gridvalue=self['default']
        minfont=self['font.scale down to']
        width=self['width']
        height=self['height']
        multiline=self['multi line']
        wrapped_text=gridvalue
        if minfont:#ok to downsize
            #First, see if text in one line is ok
            w,h=dc.GetTextExtent(gridvalue)
            while not(w<=width and h<=height):#keep getting smaller
                #Wrap Text
                if multiline:
                    wrapped_text=wordwrap(gridvalue, width, dc, breakLongWords=True, margin=0)
                else:
                    wrapped_text=gridvalue
                font=font.MakeSmaller()
                if font.PointSize<minfont:
                    break
                w,h,lh=dc.GetMultiLineTextExtent(wrapped_text,font)
                dc.Font=font
        _r=wx.Rect(0,0,width,height)
        align=0
        if self['alignment'] is not None:
            for x in self['alignment']:
                align|=getattr(wx,'ALIGN_'+x.replace('middle','center').upper())
        dc.DrawLabel(wrapped_text,_r, align)

class SymbolTxtElement(TxtElement):
    Type="symbols"
    specific_params=[
        ('symbols',['symbols',None]),
        
    
    ]
class ChoiceElement(GameField):
    Type='choice'
    choice_template="	choice:	%s"
    specific_params=[
        #('initial',['str','']),
        ('choices',['list',None]),
        ('default',['str',None]),
        ('script',['str',None]),
        ('popup style',['choice',None,'style']),
        ('render style',['choice',None,'style']),
        ('alignment',['mchoices',None,'style']),
        ("font",['font',wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)]),
        ("choice images",['imglist',None,'style']),
        ('multiple',['bool',None]),
    ]
    
    def fromObj(self,obj):
        GameField.fromObj(self,obj)
        _vs=obj.GetValues()
        self._choices=_vs['choices']
        self.params['choices']=Parameter('list',None)
        self.params['default']=Parameter('list',None)
        if _vs['multiple']:
            self.choice_template="	mchoice:	%s"
        if _vs['choice images']:
            self._choices=_vs['choice images']
            self.params['choice images']=Parameter('imglist',None,'style')
    
    def toGameText(self):
        string=GameField.toGameText(self)
        elts=[string]
        for c in self._choices:
            elts.append(self.choice_template%(c))
        return os.linesep.join(elts)

    def toStyleText(self):
        import os
        string=GameField.toStyleText(self)
        elts=[string]
        if hasattr(self,"_choices"):
            elts.append("\t\tchoice images:")
            import os.path
            for c in self._choices:
                elts.append("\t\t\t%s: %s"%(c,os.path.split(self._choices[c])[1]))
        return os.linesep.join(elts)

    def Draw(self,dc,gridvalue,template):
        r=self['render style']
        vs=self
        if r is None:
            render="text"
        else:
            from MSE import ENUMS
            render=ENUMS['render style'][r]
        if render=="text":
            #First handle the font
            vs=self
            Weight=getattr(wx,'FONTWEIGHT_'+self.get('font.weight').upper())
            Style=getattr(wx,'FONTSTYLE_'+vs.get('font.style').upper())
            Family=getattr(wx,'FONTFAMILY_'+vs.get('font.Family').upper())
            font= wx.Font(vs['font.size'], Family, Style, Weight, vs['font.underline'], vs['font.name'])
            pos=wx.Point(vs['left'],vs['top'])
            dc.Font=font
            dc.TextForeground=vs['font.color']
            width=vs['width']
            height=vs['height']
            if gridvalue is None:
                gridvalue=""
            _r=wx.Rect(vs['left'],vs['top'],width,height)
            align=0
            if vs['alignment'] is not None:
                for x in vs['alignment']:
                    align|=getattr(wx,'ALIGN_'+x.replace('middle','center').upper())
            dc.DrawLabel(gridvalue,_r, align)
        elif render=="image":
            if gridvalue is None:
                gridvalue=self['default']
                if gridvalue is None:
                    if vs['choices']:
                        gridvalue=vs['choices'][0]
            else:
                if type(gridvalue)==type(1):
                    gridvalue=vs['choices'][gridvalue]
                #Otherwise, just take the value as text one. enumproperty bug inside!                  
            path=vs['choice images'].get(gridvalue,"")
            import os.path
            if not os.path.isfile(path):
                #try relpath
                if template.dir and os.path.isfile(os.path.join(template.dir,path)):
                    path=os.path.join(self._template.dir,path)
                    img=wx.Image(path)
                if os.path.isfile(os.path.join(card_folder,path)):
                    path=os.path.join(card_folder,path)
                    img=wx.Image(path)                    
                else:
                    print '[Warn]: Provided source is not an image (%s).Skipping it'%(path)
                    import os.path                    
                    img=wx.Image(os.path.join('img','ImgChoose.png'))
            else:
                img=wx.Image(path)
            #This is were you would decide between rescaling the image or cropping it.
            #This is also here that you would aply a mask
            img.Rescale(vs['width'],vs['height'])
            bmp=wx.BitmapFromImage(img)
            dc.DrawBitmap (bmp, 0,0,True)

class MultipleChoiceElement(ChoiceElement):
    Type="multiple choice"

    specific_params=[
        ('direction',['mchoices',None,'style']),
        ('spacing',['int',None,'style']),
    ]
    
class SetFieldElement(GameField):
    template="""#Set Fields
set field:
	type: text
	name: Set Name
	description: Name of the Set"""

class ImgElement(GameField):
    Type='image'

    def Draw(self,dc,gridvalue,template):
        import os.path
        if self['editable']==False:
            gridvalue=self['default']
        if type(gridvalue) not in (type(""),type(unicode())):
            gridvalue=str(gridvalue)
        if not os.path.isfile(gridvalue):
            #print '[Warn]: Provided source is not an image (%s).Skipping it'%(gridvalue)
            if template.dir and os.path.isfile(os.path.join(template.dir,gridvalue)):
                path=os.path.join(self._template.dir,gridvalue)
                img=wx.Image(path)
            elif os.path.isfile(os.path.join(card_folder,gridvalue)):
                path=os.path.join(card_folder,gridvalue)
                print 'q',path
                img=wx.Image(path)           
            else:
                import os.path                    
                img=wx.Image(os.path.join('img','ImgChoose.png'))
        else:
            img=wx.Image(gridvalue)
        #This is were you would decide between rescaling the image or cropping it.
        #This is also here that you would aply a mask
        img.Rescale(self['width'],self['height'])
        bmp=wx.BitmapFromImage(img)
        dc.DrawBitmap (bmp, 0,0,True)
    
    specific_params=[
        ('default',['img',None,'style']),
    ]

class StaticImage(ImgElement):
    Type="staticimage"
    src=""
    
import inspect
FieldsClass={x.Type:x for x in locals().values() if inspect.isclass(x) and GameField in inspect.getmro(x)}
ElementsClass={getattr(x,"Type",None):x for x in locals().values() if inspect.isclass(x) and Element in inspect.getmro(x)}

def FieldFromValues(Type,vs):
    klass=ElementsClass.get(Type.lower(),None)
    if klass is None:
        raise ValueError('Unkown Type: %s'%Type)
    elt=klass()
    elt.fromValues(vs)
    elt.name=elt['name']
    return elt
