import wx
from wx.lib import ogl

#Create OGL Solution
class TW(ogl.ShapeCanvas):
    def __init__(self, parent):
        ogl.OGLInitialize()
        ogl.ShapeCanvas.__init__(self, parent)
        #self.SetBackgroundColour("LIGHT BLUE") #wx.WHITE)
        self.diagram = ogl.Diagram()
        self.SetDiagram(self.diagram)
        self.diagram.SetCanvas(self)
        self.shapes = []
        if parent.Parent:
            print_size=parent.Parent.fitting_size
        else:
            from config import print_size
        w,h=print_size
        w*=1
        h*=1
        self.SetVirtualSize(wx.Size(w,h))
        #self.SetScrollbars(20,20,55,40)
        self.SetScrollRate(20,20)
        
    def MyAddShape(self, elt, x, y, W,H):
        if elt.Type=='template':
            print 'adding shape template',elt.name,elt['card width'],elt['card height']
        brush=None        
        pen=wx.BLACK_PEN
        if elt.Type=='template':
            pen=wx.RED_PEN
        text=elt.name
        W=W or 85
        H=H or 50
        if elt.Type in ("staticimage",):
            shape=ogl.BitmapShape()
            import os.path
            if  elt['default'] and os.path.isfile(elt['default']):
                        shape=ogl.BitmapShape()
                        filename=elt['default']                        
                        #bmp=wx.Bitmap(filename)
                        #bmp=bmp.ConvertToImage().Rescale(elt['width'],elt['height']).ConvertToBitmap()
                        if elt['mask'] and os.path.isfile(elt['mask']):
                            mask=wx.Bitmap(elt['mask'])
                            bmp.SetMask(wx.Mask(mask))
                        shape.SetBitmap(bmp)
            else:
                dlg = wx.FileDialog(self, "Choose a Static Image for %s. Cancel for Dynamic."%elt.name, self.Parent.dir, "", "All Files(*.*)|*.*", wx.OPEN)
                try:
                    if dlg.ShowModal() == wx.ID_OK:
                        filename = dlg.GetPath()
                        #Change dir in parent
                        from os.path import split
                        self.Parent.dir=split(filename)[0]
                        # Your code
                        shape=ogl.BitmapShape()
                        bmp=wx.Bitmap(filename)
                        bmp=bmp.ConvertToImage().Rescale(elt['width'],elt['height']).ConvertToBitmap()
                        if elt['mask'] and os.path.isfile(elt['mask']):
                            mask=wx.Bitmap(elt['mask'])
                            bmp.SetMask(wx.Mask(mask))
                        shape.SetBitmap(bmp)
                    else:
                        shape=ogl.RectangleShape(50, 50)
                finally:
                    dlg.Destroy()
            #shape.SetSize(85,50,False)
        else:
            shape=BGMShape(elt)
            shape=ogl.RectangleShape(W,H)
        ########if elt.Type in ("image",):
        ########    import os.path
        ########    if  elt['default'] and os.path.isfile(elt['default']):
        ########        shape=ogl.BitmapShape()
        ########        filename=elt['default']                        
        ########        bmp=wx.Bitmap(filename)
        ########        bmp=bmp.ConvertToImage().Rescale(elt['width'],elt['height']).ConvertToBitmap()
        ########        if elt['mask'] and os.path.isfile(elt['mask']):
        ########            mask=wx.Bitmap(elt['mask'])
        ########            bmp.SetMask(wx.Mask(mask))
        ########        shape.SetBitmap(bmp)
        ########    else:
        ########        shape=ogl.RectangleShape(50, 50)           
        ########elif elt.Type in ('Set','Info'):
        ########    shape=ogl.Shape()
        ########else:
        ########    shape=ogl.RectangleShape(W, H)
        if elt.Type!='template':
            shape.SetDraggable(True, True)
        else:
            shape.SetDraggable(False,False)
        shape.SetCanvas(self)
        shape.SetX(x)
        shape.SetY(y)
        #Custom stuff
        shape.text=text
        if pen:    shape.SetPen(pen)
        if brush:  shape.SetBrush(brush)
        if text:
            if elt.Type not in ('staticimage',):
                for line in text.split('\n'):
                    shape.AddText(line)
        #shape.SetShadowMode(ogl.SHADOW_RIGHT)
        self.diagram.AddShape(shape)
        shape.Show(True)

        evthandler = MyEvtHandler()
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)

        self.shapes.append(shape)
        shape.SetCentreResize(False)
        shape.elt=elt
        if elt.Type=="template":
            print 'done adding',elt['card width'],elt['card height']
        return shape

class MyEvtHandler(ogl.ShapeEvtHandler):
            def __init__(self, ):
                ogl.ShapeEvtHandler.__init__(self)
            
            def OnLeftDoubleClick(self,x,y,keys=0,attachmen=0):
                shape=self.GetShape()
                diagram=shape.GetCanvas().GetDiagram()
                diagram.RemoveShape(shape)
                diagram.InsertShape(shape)
                shape.GetCanvas().Refresh()

            def OnLeftClick(self, x, y, keys=0, attachment=0):
                shape = self.GetShape()
                canvas = shape.GetCanvas()
                dc = wx.ClientDC(canvas)
                canvas.PrepareDC(dc)
                if shape.Selected():
                    shape.Select(False, dc)
                    #canvas.Redraw(dc)
                    canvas.Refresh(False)
                else:
                    redraw = False
                    shapeList = canvas.GetDiagram().GetShapeList()
                    toUnselect = []
                    for s in shapeList:
                        if s.Selected():
                            # If we unselect it now then some of the objects in
                            # shapeList will become invalid (the control points are
                            # shapes too!) and bad things will happen...
                            toUnselect.append(s)
                    shape.Select(True, dc)
                    if toUnselect:
                        for s in toUnselect:
                            s.Select(False, dc)
                        ##canvas.Redraw(dc)
                        canvas.Refresh(False)
                canvas = shape.GetCanvas()
                canvas.Parent.tree.SelectItem(self.GetShape()._treeitem)
                canvas.Parent.UpdateInfo()
                
            def OnEndDragLeft(self, x, y, keys=0, attachment=0):
                shape = self.GetShape()
                ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)
                if not shape.Selected():
                    self.OnLeftClick(x, y, keys, attachment)
                canvas = shape.GetCanvas()
                canvas.Parent.tree.SelectItem(self.GetShape()._treeitem)
                canvas.Parent.UpdateInfo()
                
            def OnSizingEndDragLeft(self, pt, x, y, keys, attch):

                ogl.ShapeEvtHandler.OnSizingEndDragLeft(self, pt, x, y, keys, attch)

                    
                canvas = self.GetShape().GetCanvas()
                thelist=canvas.GetDiagram().GetShapeList()
                #Select the node from shape - this trigger updae info
                canvas.Parent.tree.SelectItem(self.GetShape()._treeitem)
                canvas.Parent.UpdateInfo()
                
            def OnMovePost(self, dc, x, y, oldX, oldY, display):
                shape = self.GetShape()
                ogl.ShapeEvtHandler.OnMovePost(self, dc, x, y, oldX, oldY, display)

class BGMShape(ogl.DrawnShape):
    def __init__(self,element):
        ogl.DrawnShape.__init__(self)
        self.element=element
        
    def OnDraw(self, dc):
        # Pass pen and brush in case we have force outline
        # and fill colours
        if self._shadowMode != 0:
            if self._shadowBrush:
                self._metafiles[self._currentAngle]._fillBrush = self._shadowBrush
            self._metafiles[self._currentAngle]._outlinePen = wx.Pen(wx.WHITE, 1, wx.TRANSPARENT)
            self._metafiles[self._currentAngle].Draw(dc, self._xpos + self._shadowOffsetX, self._ypos + self._shadowOffsetY)
        #replace {} by _values at some point
        #some for gridvalue, here elt.name
        from actions import template_empty
        self.element.Render("",dc,template_empty,{},isPaint=True)