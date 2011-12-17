"Define a simple panel able to fetch data from BGG"

import wx,sys
import wx.lib.agw.buttonpanel as bp

from urllib import urlretrieve

from BeautifulSoup import BeautifulSoup as BS

USE_PROXY=False
from time import clock
startup=clock()

from config import bgg_img_browse_url, bgg_file_browse_url, bgg_link_browse_url
    
def install_proxy():
    USE_PROXY=True
    import urllib2 
    global urlretrieve
    proxy_handler = urllib2.ProxyHandler({'http': 'http://proxy.cma-cgm.com:8080/'})
    proxy_auth_handler = urllib2.ProxyBasicAuthHandler()
    #proxy_auth_handler.add_password('realm', 'host', 'username', 'password')
    opener = urllib2.build_opener(proxy_handler, proxy_auth_handler)
    # This time, rather than install the OpenerDirector, we use it directly:
    urlretrieve=opener.open

if __name__=='__main__':
    PARENT=wx.Frame
else:
    PARENT=wx.Panel
    
class BGGFrame(PARENT):
    def __init__(self,*args):
        PARENT.__init__(self,*args)
        self.Title="BGG Image Browser"
        self.TargetDir="."
        if self.Parent:
            self.TargetDir=self.Parent.dir
            self.Size=wx.Size(300,800)
        self.Sizer=wx.BoxSizer(wx.VERTICAL)
        self.titleBar = bp.ButtonPanel(self, -1, "Game Name ",agwStyle=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)
        #
        #Game ID Field
        self.search = wx.SearchCtrl(self.titleBar,style=wx.TE_PROCESS_ENTER)
        self.search.Bind(wx.EVT_TEXT_ENTER, self.OnSearch)
        self.search.Value=""
        self.titleBar.AddControl(self.search)
        self.Sizer.Add(self.titleBar,0,wx.EXPAND|wx.ALL,0)
        #Bottom item
        box=wx.BoxSizer()
        if self.Parent:
            box=wx.BoxSizer(wx.VERTICAL)
        #Result List
        self.results=wx.TreeCtrl(self)
        self.root=self.results.AddRoot('Results')
        self.results.Bind(wx.EVT_TREE_ITEM_ACTIVATED,self.OnResultsActivated)
        self.results.Bind(wx.EVT_TREE_SEL_CHANGED,self.OnResultsChanged)
        box.Add(self.results,1,wx.EXPAND|wx.LEFT|wx.RIGHT,0)
        #Imgs second
        #self.wsizer=s=wx.WrapSizer()
        self.psizer=s=wx.BoxSizer(wx.VERTICAL)
        box.Add(s, 2, wx.EXPAND|wx.LEFT|wx.RIGHT, 0)
        #subsizr for all listboxes
        subs=wx.BoxSizer(wx.HORIZONTAL)
        s.Add(subs,2,wx.EXPAND|wx.ALL,0)
        #Box add multiple checkbox list
        self.lb = wx.CheckListBox(self, -1, (80, 50), wx.DefaultSize, [])
        subs.Add(self.lb,2,wx.EXPAND|wx.LEFT|wx.RIGHT, 0)
        self.filelist = wx.CheckListBox(self, -1, (80, 50), wx.DefaultSize, [])
        subs.Add(self.filelist,2,wx.EXPAND|wx.LEFT|wx.RIGHT, 0)
        self.linklist = wx.CheckListBox(self, -1, (80, 50), wx.DefaultSize, [])
        subs.Add(self.linklist,2,wx.EXPAND|wx.LEFT|wx.RIGHT, 0)
        ####Box add sort filter
        ###self.filterchoice=wx.Choice(self,-1,choices=['recent','Hot'])
        ###self.filterchoice.SetSelection(0)
        ###s.Add(self.filterchoice,0,wx.EXPAND|wx.LEFT|wx.RIGHT, 0)
        ####Box add categ filter
        ###self.filtercateg=wx.Choice(self,-1,choices=['all','Component','Box Front'])
        ###self.filtercateg.SetSelection(0)
        ###s.Add(self.filtercateg,0,wx.EXPAND|wx.LEFT|wx.RIGHT, 0)
        #Add the BoxSize
        self.Sizer.Add(box,1,wx.EXPAND|wx.LEFT|wx.RIGHT, 0)
        box=wx.BoxSizer(wx.HORIZONTAL)
        self.Sizer.Add(box,0,wx.ALIGN_CENTER_HORIZONTAL|wx.ALL,0)
        #Download button last
        self.button=wx.Button(self,-1,"Generate Image Page")
        self.button.Bind(wx.EVT_BUTTON,self.OnDownload)
        box.Add(self.button,0,wx.EXPAND|wx.LEFT|wx.RIGHT,0)
        #Download button last
        self.button2=wx.Button(self,-1,"Generate File Page")
        self.button2.Bind(wx.EVT_BUTTON,self.OnDownloadFile)
        box.Add(self.button2,0,wx.EXPAND|wx.LEFT|wx.RIGHT,0)
        #Download button last
        self.button3=wx.Button(self,-1,"Generate Link Page")
        self.button3.Bind(wx.EVT_BUTTON,self.OnDownloadLink)
        box.Add(self.button3,0,wx.EXPAND|wx.LEFT|wx.RIGHT,0)
        #STB
        if self.Parent:
            self.stb=self.Parent.statusBar1
        else:
            self.stb=self.CreateStatusBar(style=wx.STB_SIZEGRIP)
        self.titleBar.DoLayout()
        self.Layout()
        self.imgs=[]
        self.currentgame=None
        self.currentfile=""

    def OnResultsChanged(self,evt):
        item=self.results.Selection
        data=self.results.GetPyData(item)
        if data:
                wx.BeginBusyCursor()
                self.stb.SetStatusText( 'Fetching %s imgs info....'%(self.results.GetItemText(item)))
                
                urls=[ bgg_img_browse_url,bgg_file_browse_url, bgg_link_browse_url]
                widgets=[self.lb,self.filelist,self.linklist]
                for url,widget in zip(urls,widgets):
                    src=urlretrieve(url%(int(data),1))
                    src=src[0]
                    bs=BS(file(src).read())
                    imgs=[x.get('src') for x in bs.findAll('img',{"class":None})]
                    try:
                        total=int(bs.findAll('div',{"class":'pages'})[0].contents[0].split('of ')[-1])
                    except:
                        try:
                            #Pure hack to compensate the facct the html for links are differents
                            txt=bs.findAll('div',{"class":'pages'})[0].contents[0].split('of ')[-1].strip()
                            total=int(txt.split(';')[-1])
                        except ValueError:
                            print 'Issue with', txt.split(';')[-1]
                            total=10
                    widget.Set([str(x+1) for x in range(total)])
                wx.EndBusyCursor()
                self.currentgame=data
        
    def OnResultsActivated(self,evt):
        item=self.results.Selection
        data=self.results.GetPyData(item)
        if data:
            #Remove all item from wrapped stuf
            if data!=self.currentgame:
                self.currentfile=""
            self.GenPage(data)
            self.currentgame=data
    
    def GenPage(self,gameId,pageId=1,START=True,typ='Images'):
        wx.BeginBusyCursor()
        self.stb.SetStatusText( 'Fetching %s imgs page %s....'%(gameId,pageId))
        urls={
            'Images':bgg_img_browse_url,
            'Files':bgg_file_browse_url,
            'Links':bgg_link_browse_url,
        }
        url=urls[typ]
        src=urlretrieve(url%(int(gameId),int(pageId)))
        src=src[0]
        texts=["<h1>%s of %s (#%s) - Page %d</h1>"%(typ,self.results.GetItemText(self.results.Selection),gameId,pageId),'<ol>']
        if typ=="Images":
            bs=BS(file(src).read())
            imgs=[x.get('src') for x in bs.findAll('img',{"class":None})]
            for index,img in enumerate(imgs):
                href=img.replace('_mt.jpg','.jpg')
                img=img.replace('_mt.jpg','_t.jpg')
                texts.append('%d:<a href="%s"><img src="%s"></a></li>'%(index,href,img))
            texts.append('</ol>')
        else:
            texts.append(file(src).read().decode('cp1252'))
            texts.append('</ol>')
        #texts.append('<div align="center"><input type="button" value"Download Selected"></div></form>')
        from tempfile import mktemp
        from os import linesep,startfile
        if not self.currentfile:
            dst=mktemp(suffix=".html")
            file(dst,'wb').write(linesep.join(texts).encode('cp1252'))
            self.currentfile=dst
        else:
            dst=self.currentfile
            file(dst,'ab').write(linesep.join(texts).encode('cp1252'))
        wx.EndBusyCursor()
        if START:
            startfile(self.currentfile)
        
    def OnDownload(self,evt):
        pageIds=[x+1 for x in self.lb.GetChecked()]
        #retrieve all page for each gameId
        for pageId in pageIds:
            self.GenPage(self.currentgame,pageId,START=False,typ="Images")
        from os import startfile
        startfile(self.currentfile)
        self.stb.SetStatusText('Done !')

    def OnDownloadLink(self,evt):
        pageIds=[x+1 for x in self.linklist.GetChecked()]
        #retrieve all page for each gameId
        for pageId in pageIds:
            self.GenPage(self.currentgame,pageId,START=False,typ="Links")
        from os import startfile
        startfile(self.currentfile)
        self.stb.SetStatusText('Done !')
        
    def OnDownloadFile(self,evt):
        pageIds=[x+1 for x in self.filelist.GetChecked()]
        #retrieve all page for each gameId
        for pageId in pageIds:
            self.GenPage(self.currentgame,pageId,START=False,typ="Files")
        from os import startfile
        startfile(self.currentfile)
        self.stb.SetStatusText('Done !')
                
    def OnSearch(self,evt):
        gameName=self.search.Value
        wx.BeginBusyCursor()
        from urllib import quote
        from xml.etree import cElementTree as ET
        from config import bgg_search_url
        target=bgg_search_url%quote(gameName)
        self.stb.SetStatusText('Searching for game named %s'%gameName)
        if not USE_PROXY:
            xml=ET.parse(urlretrieve(target)[0])
        else:
            xml=ET.fromstring(urlretrieve(target).read())
        bgs=xml.findall('boardgame')
        self.results.DeleteAllItems()
        self.root=self.results.AddRoot('Results for %s:'%gameName)
        for bg in bgs:
            try:
                name,year=bg.getchildren()
            except ValueError:
                name=bg.getchildren()[0]
                year=""
            if year:
                item=self.results.AppendItem(self.root,"%s (%s)"%(name.text,year.text))
            else:
                item=self.results.AppendItem(self.root,"%s"%(name.text))
            self.results.SetPyData(item,bg.get('objectid'))
        self.results.Expand(self.root)
        self.stb.SetStatusText('Found %d result(s) for %s'%(len(bgs),gameName))
        wx.EndBusyCursor()
        
if __name__=='__main__':
    app=wx.PySimpleApp()
    f=BGGFrame(None)
    f.Show()
    app.MainLoop()