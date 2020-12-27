import wx
import wx.lib.ogl as ogl
import random

# tested on wxPython 2.8.11.0, Python 2.7.1+, Ubuntu 11.04

# started from:
# http://stackoverflow.com/questions/25756896/drawing-to-panel-inside-of-frame-in-wxpython/27804975#27804975

# see also:
# wxPython-2.8.11.0-demo/demo/OGL.py
# https://www.daniweb.com/software-development/python/threads/186203/creating-editable-drawing-objects-in-wxpython
# http://gscept.com/svn/Docs/PSE/Milestone%203/code/trunk/python_test/src/oglEditor.py
# http://nullege.com/codes/search/wx.lib.ogl.Diagram
# http://nullege.com/codes/show/src%40w%40e%40web2cms-HEAD%40web2py%40gluon%40contrib%40pyfpdf%40designer.py/465/wx.lib.ogl.Diagram/python
# https://www.daniweb.com/software-development/python/threads/204969/setfocus-on-canvas-not-working
# http://stackoverflow.com/questions/3538769/how-do-you-draw-a-grid-and-rectangles-in-python
# http://stackoverflow.com/questions/7794496/snapping-to-pixels-in-wxpython


# ogl.ShapeCanvas must go first, else TypeError:  Cannot create a consistent method resolution
class MyPanel(ogl.ShapeCanvas, wx.Panel):#(wx.PyPanel): #PyPanel also works
  def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name="MyPanel"):
    super(MyPanel, self).__init__(parent, id, pos, size, style, name)
    self.gridsize = 20 # in pixels
    # must have these (w. Diagram) if using ogl.ShapeCanvas:
    self.diagram = ogl.Diagram()
    self.SetDiagram(self.diagram)
    self.diagram.SetCanvas(self)
    # set up snap to grid - note, like this it works only for drag (relative to shape center), not for resize via handles!
    self.diagram.SetGridSpacing( self.gridsize )
    self.diagram.SetSnapToGrid( True )
    # initialize array of shapes with one element
    self.shapes = []
    self.MyAddShape(
      ogl.CircleShape(85), # diameter - drag marquee will not be visible if (diameter mod gridsize == 0), as it will overlap with the grid lines
      60, 60, wx.Pen(wx.BLUE, 3), wx.GREEN_BRUSH, "Circle"
      )
    self.Bind(wx.EVT_SIZE, self.OnSize)
    self.Bind(wx.EVT_PAINT, self.OnPaint)
    wx.EVT_KEY_DOWN(self, self.OnKeyPressedM)
  def OnKeyPressedM(self, event):
    keyCode = event.GetKeyCode()
    print("MyPanel.OnKeyPressedM: %d"%(keyCode) )
    # insert a rectangle here on [SPACE]:
    if keyCode == wx.WXK_SPACE:
      randx = random.randint(1, 300)
      randy = random.randint(1, 200)
      if self.diagram.GetSnapToGrid():
        randx, randy = self.Snap(randx, randy) # must do snapping (if desired) manually, here at insertion!
      self.MyAddShape(
          ogl.RectangleShape(60, 20),
          randx, randy, wx.BLACK_PEN, wx.LIGHT_GREY_BRUSH, "Rect %d"%(len(self.shapes))
        )
      self.Refresh(False)
    event.Skip() # must have this, to have the MyFrame.OnKeyPressed trigger as well!
  def OnSize(self, event):
    #print("OnSize" +str(event))
    self.Refresh() # must have here!
    event.Skip()
  def DrawBackgroundGrid(self):
    dc = wx.PaintDC(self)
    #print(dc)
    rect = self.GetClientRect()
    rx, ry, rw, rh = rect
    dc.SetBrush(wx.Brush(self.GetForegroundColour()))
    dc.SetPen(wx.Pen(self.GetForegroundColour()))
    # draw ("tile") the grid
    x = rx
    while x < rx+rw:
      y = ry
      dc.DrawLine(x, ry, x, ry+rh) # long (vertical) lines
      while y < ry+rh:
        dc.DrawLine(x, y, x+self.gridsize, y) # short (horizontal) lines
        y = y + self.gridsize
      x = x + self.gridsize
  def OnPaint(self, event):
    dc = wx.PaintDC(self) # works
    self.DrawBackgroundGrid()
    # self.Refresh() # recurses here - don't use!
    # self.diagram.GetCanvas().Refresh() # blocks here - don't use!
    self.diagram.GetCanvas().Redraw(dc) # this to redraw the elements on top of the grid, drawn just before
  # MyAddShape is from OGL.py:
  def MyAddShape(self, shape, x, y, pen, brush, text):
    # Composites have to be moved for all children to get in place
    if isinstance(shape, ogl.CompositeShape):
      dc = wx.ClientDC(self)
      self.PrepareDC(dc)
      shape.Move(dc, x, y)
    else:
      shape.SetDraggable(True, True)
    shape.SetCanvas(self)
    shape.SetX(x)
    shape.SetY(y)
    if pen:  shape.SetPen(pen)
    if brush:  shape.SetBrush(brush)
    if text:
      for line in text.split('\n'):
        shape.AddText(line)
    #shape.SetShadowMode(ogl.SHADOW_RIGHT)
    self.diagram.AddShape(shape)
    shape.Show(True)
    evthandler = MyEvtHandler(self)
    evthandler.SetShape(shape)
    evthandler.SetPreviousHandler(shape.GetEventHandler())
    shape.SetEventHandler(evthandler)
    self.shapes.append(shape)
    return shape

# copyfrom OGL.pyl; modded
class MyEvtHandler(ogl.ShapeEvtHandler):
  def __init__(self, parent): #
    ogl.ShapeEvtHandler.__init__(self)
    self.parent = parent
  def UpdateStatusBar(self, shape):
    x, y = shape.GetX(), shape.GetY()
    width, height = shape.GetBoundingBoxMax()
    self.parent.Refresh(False) # do here, to redraw the background after a drag move, or scale of shape
    print("Pos: (%d, %d)  Size: (%d, %d)" % (x, y, width, height))
  def OnLeftClick(self, x, y, keys=0, attachment=0):
    # note: to deselect a selected shape, don't click the background, but click the shape again
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
    self.UpdateStatusBar(shape)
  def OnEndDragLeft(self, x, y, keys=0, attachment=0):
    shape = self.GetShape()
    ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)
    if not shape.Selected():
      self.OnLeftClick(x, y, keys, attachment)
    self.UpdateStatusBar(shape)
  def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
    ogl.ShapeEvtHandler.OnSizingEndDragLeft(self, pt, x, y, keys, attch)
    self.UpdateStatusBar(self.GetShape())
  def OnMovePost(self, dc, x, y, oldX, oldY, display):
    shape = self.GetShape()
    ogl.ShapeEvtHandler.OnMovePost(self, dc, x, y, oldX, oldY, display)
    self.UpdateStatusBar(shape)
    if "wxMac" in wx.PlatformInfo:
      shape.GetCanvas().Refresh(False)
  def OnRightClick(self, *dontcare):
    #self.log.WriteText("%s\n" % self.GetShape())
    print("OnRightClick")

class MyFrame(wx.Frame):
  def __init__(self, parent):
    wx.Frame.__init__(self, parent, -1, "Custom Panel Grid Demo")
    # This creates some pens and brushes that the OGL library uses.
    # (else "global name 'BlackForegroundPen' is not defined")
    # It should be called after the app object has been created, but
    # before OGL is used.
    ogl.OGLInitialize()
    self.SetSize((300, 200))
    self.panel = MyPanel(self) #wx.Panel(self)
    self.panel.SetBackgroundColour(wx.Colour(250,250,250))
    self.panel.SetForegroundColour(wx.Colour(127,127,127))
    sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
    sizer_1.Add(self.panel, 1, wx.EXPAND | wx.ALL, 0)
    self.SetSizer(sizer_1)
    self.SetAutoLayout(1)
    self.Layout()
    self.Show(1)
    # NOTE: on my dev versions, using ogl.Diagram causes _all_
    # key press events, from *anywhere*, to stop propagating!
    # Doing a .SetFocus on the ogl.ShapeCanvas panel,
    # finally makes the Key events propagate!
    # (troubleshoot via run.py from wx python demo)
    self.panel.SetFocus()
    self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyPressed) # EVT_CHAR_HOOK EVT_KEY_DOWN
  def OnKeyPressed(self, event):
    print("MyFrame.OnKeyPressed (just testing)")

app = wx.App(0)
frame = MyFrame(None)
app.SetTopWindow(frame)
frame.Show()
app.MainLoop()