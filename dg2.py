import wx
import wx.lib.ogl as ogl

CLICK_TO_DRAG = True

class MyEvtHandler(ogl.ShapeEvtHandler):
        """
        Overwrite the default event handler to implement some custom features. 
        """
        def __init__(self):
                ogl.ShapeEvtHandler.__init__(self)

        def OnLeftClick(self, x, y, keys = 0, attachment = 0):
                """
                The dragging is done here. 
                """
                shape = self.GetShape()
                print (shape.__class__, shape.GetClassName(), shape.a)
                canvas = shape.GetCanvas()
                dc = wx.ClientDC(canvas)
                canvas.PrepareDC(dc)
                
                if shape.Selected():
                        shape.Select(False, dc)
                        canvas.Redraw(dc)
                else:
                        redraw = False
                        shapeList = canvas.GetDiagram().GetShapeList()
                        toUnselect = []
                        for s in shapeList:
                                if s.Selected():
                                        toUnselect.append(s)

                        shape.Select(True, dc)
                        
                        if toUnselect:
                                for s in toUnselect:
                                        s.Select(False, dc)
                                canvas.Redraw(dc)



class OGLCanvas(ogl.ShapeCanvas):
        def __init__(self, parent, frame):
                ogl.ShapeCanvas.__init__(self, parent)
                
                self.SetBackgroundColour("LIGHT BLUE")
                self.diagram = ogl.Diagram()
                self.SetDiagram(self.diagram)
                self.diagram.SetCanvas(self)
                
                self.circle = ogl.CircleShape(100)
                self.circle.SetCanvas(self)
                self.circle.a="Circle identified"
                self.diagram.AddShape(self.circle)
                self.circle.Show(True)
                
                if CLICK_TO_DRAG:
                        self.evthandler = MyEvtHandler()
                        self.evthandler.SetShape(self.circle)
                        self.evthandler.SetPreviousHandler(self.circle.GetEventHandler())
                        self.circle.SetEventHandler(self.evthandler)
                else:
                        self.Bind(wx.EVT_MOTION, self.OnMotion, self)

        def OnMotion(self, event):
                shape = self.circle
                
                bx = shape.GetX()
                by = shape.GetY()
                bw, bh = shape.GetBoundingBoxMax()
                oldrect = wx.Rect(int(bx-bw/2)-1, int(by-bh/2)-1, int(bw)+2, int(bh)+2)
                
                canvas = shape.GetCanvas()
                dc = wx.ClientDC(canvas)
                canvas.PrepareDC(dc)
                
                shape.Move(dc, event.GetPosition()[0], event.GetPosition()[1])
                canvas.Refresh(False, oldrect)
                event.Skip()


class OGLFrame(wx.Frame):
        def __init__(self, *args, **kwds):
                wx.Frame.__init__(self, *args, **kwds)
                
                self.SetTitle("OGL TEST")
                self.SetBackgroundColour(wx.Colour(8, 197, 248))
                self.canvas = OGLCanvas(self, self)

if __name__ == "__main__":
        app = wx.PySimpleApp(False)
        wx.InitAllImageHandlers()
        ogl.OGLInitialize()
        frame = OGLFrame(None, -1, "")
        app.SetTopWindow(frame)
        frame.Show(True)
        app.MainLoop()