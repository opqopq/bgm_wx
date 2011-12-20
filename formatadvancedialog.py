import wx.lib.delayedresult as DR
import wx

class FormatAdvanceDialog(wx.Frame):
    def __init__(self, parent,title,dir):
        wx.Frame.__init__(self, parent,title=title)
        self.dir=dir
        pnl = wx.Panel(self)
        self.checkboxUseDelayed = wx.CheckBox(pnl, -1, "Using delayedresult")
        self.buttonGet = wx.Button(pnl, -1, "Get")
        self.buttonAbort = wx.Button(pnl, -1, "Abort")
        self.slider = wx.Slider(pnl, -1, 0, 0, 10, size=(100,-1),
                                style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS)
        self.textCtrlResult = wx.TextCtrl(pnl, -1, "", style=wx.TE_READONLY)

        self.checkboxUseDelayed.SetValue(1)
        self.checkboxUseDelayed.Enable(False)
        self.buttonAbort.Enable(False)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        vsizer.Add(self.checkboxUseDelayed, 0, wx.ALL, 10)
        hsizer.Add(self.buttonGet, 0, wx.ALL, 5)
        hsizer.Add(self.buttonAbort, 0, wx.ALL, 5)
        hsizer.Add(self.slider, 0, wx.ALL, 5)
        hsizer.Add(self.textCtrlResult, 0, wx.ALL, 5)
        vsizer.Add(hsizer, 0, wx.ALL, 5)
        pnl.SetSizer(vsizer)
        vsizer.SetSizeHints(self)
        
        self.Bind(wx.EVT_BUTTON, self.handleGet, self.buttonGet)
        self.Bind(wx.EVT_BUTTON, self.handleAbort, self.buttonAbort)
        self.jobID = 0
        self.abortEvent = DR.AbortEvent()
        self.Bind(wx.EVT_CLOSE, self.handleClose)

    def handleClose(self, event):
        """Only needed because in demo, closing the window does not kill the 
        app, so worker thread continues and sends result to dead frame; normally
        your app would exit so this would not happen."""
        if self.buttonAbort.IsEnabled():
            self.abortEvent.set()
        self.Destroy()
            
    def handleGet(self, event): 
        """Compute result in separate thread, doesn't affect GUI response."""
        self.buttonGet.Enable(False)
        self.buttonAbort.Enable(True)
        self.abortEvent.clear()
        self.jobID += 1
        
        DR.startWorker(self._resultConsumer, self._resultProducer, 
                                  wargs=(self.jobID,self.abortEvent), jobID=self.jobID)

    def _resultProducer(self, jobID, abortEvent):
        """Pretend to be a complex worker function or something that takes 
        long time to run due to network access etc. GUI will freeze if this 
        method is not called in separate thread."""
        import pdfprinter
        total= self.Parent.deckgrid.GetDeckSize()
        for i in pdfprinter.format(self.Parent.GetCurrentDeck(),self.dir,self.Parent.deckname,fitting_size=self.Parent.fitting_size,templates=self.Parent.templates):
            self.textCtrlResult.SetValue('%d on %d'%((i+1),total))
            if abortEvent():
                break
        return jobID

    def handleAbort(self, event): 
        """Abort the result computation."""
        self.buttonGet.Enable(True)
        self.buttonAbort.Enable(False)
        self.abortEvent.set()

    def _resultConsumer(self, delayedResult):
        jobID = delayedResult.getJobID()
        assert jobID == self.jobID
        try:
            result = delayedResult.get()
        except Exception, exc:
            print "Result for job %s raised exception: %s" % (jobID, exc) 
            return
        
        # output result
        self.textCtrlResult.SetValue(str(result))
        
        
        # get ready for next job:
        self.buttonGet.Enable(True)
        self.buttonAbort.Enable(False)

