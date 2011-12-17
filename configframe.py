import wx
from config import __all__ as CONFIG_ITEMS
import config

class ConfigDialog(wx.Frame):
    def __init__(self,*args):
        wx.Frame.__init__(self,*args)
        self.Title="Configuration Dialog"
        self.Build()
        
    def Build(self):
        pass
        
    