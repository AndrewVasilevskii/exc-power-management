import wx
import sqlite3
from model.database import createTablesIfNotExists, getGraphs, insertGraph, updateGraph, deleteGraph
import config

class GraphSettings(wx.Frame):

    def __init__(self, parent):
        # ensure the parent's __init__ is called
        size = wx.Size(700, 300)
        self.parent=parent
        self.parent.Enable(False)
        parentPos = self.parent.GetPosition()
        wx.Frame.__init__(self, parent, title="Graph Settings", pos=(parentPos[0]+config.childFrameDisplacement[0], parentPos[1]+config.childFrameDisplacement[1]), style=config.childFrameStyle, size=size)
        icon = wx.Icon('bitmaps/app.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.Bind(wx.EVT_CLOSE, self.OnChancelPressed)
        # create a panel in the frame
        self.SetMinSize(size)
        self.panel = wx.Panel(self)

        self.series = []
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        # create some sizers
        self.serialSizer = wx.BoxSizer(wx.VERTICAL)
        
        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
      
        btn = wx.Button(self.panel, label="Add")
        btn.Bind(wx.EVT_BUTTON, self.OnAddPressed)
        buttonsSizer.Add(btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        btn = wx.Button(self.panel, label="Cancel")
        btn.Bind(wx.EVT_BUTTON, self.OnChancelPressed)
        buttonsSizer.Add(btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        btn = wx.Button(self.panel, label="Redraw")
        btn.Bind(wx.EVT_BUTTON, self.OnRedrawPressed)
        buttonsSizer.Add(btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
      
        self.mainSizer.Add(self.serialSizer, 0, wx.ALL|wx.ALIGN_LEFT, 0)
        self.mainSizer.Add(buttonsSizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)

        self.panel.SetSizer(self.mainSizer)
        self.colors = ["red", "green", "blue", "yellow"]
        self.colorsLabel = ["r", "g", "b", "y"]
        self.poss = ["Left", "Right"]
        
        self.db = sqlite3.connect('db.sqlite')
    
        createTablesIfNotExists(self.db)
        
        self.graphs = getGraphs(self.db)
        
        for gr in self.graphs:
            self.addGraph(gr[2], gr[1], gr[3], gr[0])

       
    def OnAddPressed(self, event):
        self.addGraph("red", 5000, 0, -1)
        
    def addGraph(self, color, mass, pos, dbindex):
        if pos == -1:
            pos = 0
        newSerialSizer = wx.BoxSizer(wx.HORIZONTAL)
        size = wx.Size(100, 27)
        selectColorText = wx.StaticText(self.panel, label="Select Color:")
        ind = 0
        for index, clr in enumerate(self.colorsLabel):
            if color == clr:
                color = clr
                ind = index
        selectColorBox = wx.ComboBox(self.panel, size=size, value=color, choices=self.colors)
        selectColorBox.SetSelection(ind)
        selectColorBox.SetEditable(False)
        selectMassText = wx.StaticText(self.panel, label="Select Mass:")
        selectMassCtrl = wx.TextCtrl(self.panel, size=(70, -1))
        selectMassCtrl.SetLabel(str(mass))
        selectPosText = wx.StaticText(self.panel, label="Position:")
        
        selectPosBox = wx.ComboBox(self.panel, size=size, value=self.poss[pos], choices=self.poss)
        selectPosBox.Select(pos)
        selectPosBox.SetEditable(False)
        btn = wx.Button(self.panel, label="Remove")
        btn.Bind(wx.EVT_BUTTON, self.OnRemovePressed)
        newSerialSizer.Add(selectMassText, 0, wx.ALL, 5)
        newSerialSizer.Add(selectMassCtrl, 0, wx.ALL, 5)
        newSerialSizer.Add(selectColorText, 0, wx.ALL, 5)
        newSerialSizer.Add(selectColorBox, 0, wx.ALL, 5)
        newSerialSizer.Add(selectPosText, 0, wx.ALL, 5)
        newSerialSizer.Add(selectPosBox, 0, wx.ALL, 5)
        newSerialSizer.Add(btn, 0, wx.ALL, 5)
        self.serialSizer.Add(newSerialSizer)
        newSerialSizer.Layout()
        self.mainSizer.Layout()
        self.Fit()
        inst = {"sizer": newSerialSizer, "btn": btn, "mass": selectMassCtrl, "color": selectColorBox, "position": selectPosBox, "index": dbindex}
        self.series.append(inst)


    def OnChancelPressed(self, event):
        self.parent.Enable(True)
        self.db.close()
        self.Hide()
        self.parent.SetFocus()
        
    def OnRemovePressed(self, event):
        btn = event.GetEventObject()
        for index, obj in enumerate(self.series):
            if obj["btn"] == btn:
                self.serialSizer.Hide(obj["sizer"], recursive=True)
                self.serialSizer.Remove(obj["sizer"])
                self.serialSizer.Layout()
                self.mainSizer.Layout()
                self.series.pop(index)
                if obj["index"] != -1:
                    deleteGraph(self.db, obj["index"])
                return
                
    
    def OnRedrawPressed(self, event):
        for inst in self.series:
            selectMassCtrl = inst["mass"]
            selectColorBox = inst["color"]
            selectPosBox = inst["position"]
            index = inst["index"]
            
            strVal = selectMassCtrl.GetValue()
            mass = 0
            try:
                mass = int(strVal)
            except:
                continue
            
            pos = selectColorBox.GetSelection()
            if pos == -1:
                pos = 0
            
            if index == -1:
                try:
                    updateGraph(self.db, mass, self.colorsLabel[pos], selectPosBox.GetSelection(), index)
                except:
                    insertGraph(self.db, mass, self.colorsLabel[pos], selectPosBox.GetSelection())
            else:
                updateGraph(self.db, mass, self.colorsLabel[pos], selectPosBox.GetSelection(), index)

        self.parent.Enable(True)
        self.db.close()
        self.Hide()
        self.parent.SetFocus()
    