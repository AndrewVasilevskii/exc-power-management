import wx
import serial.tools.list_ports
import config

class PortSettings(wx.Frame):

    def __init__(self, parent):
        # ensure the parent's __init__ is called
        size = wx.Size(400, 300)
        self.parent=parent
        self.parent.Enable(False)
        parentPos = self.parent.GetPosition()
        wx.Frame.__init__(self, parent=parent, title="Port Settings", pos=(parentPos[0]+config.childFrameDisplacement[0], parentPos[1]+config.childFrameDisplacement[1]), style=config.childFrameStyle , size=size)
        icon = wx.Icon('bitmaps/app.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        # create a panel in the frame
        self.SetMinSize(size)
        self.panel = wx.Panel(self)
        self.SetFocus()

        # create some sizers
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        portSizer = wx.BoxSizer(wx.HORIZONTAL)
        baudRateSizer = wx.BoxSizer(wx.HORIZONTAL)
        paritySizer = wx.BoxSizer(wx.HORIZONTAL)
        stopBitsSizer = wx.BoxSizer(wx.HORIZONTAL)
        flowControlSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        ports = serial.tools.list_ports.comports()
        self.portsValues = []
        trimmedPorts = []

        selectedIndex = 0
        portsList = []
        for port in ports:
            if port[2] != 'n/a':
                trimmedPorts.append(port)
                portsList.append(port[1])
                self.portsValues.append(port[0])

        connectDisabled = True
        if len(portsList) > 0:
            connectDisabled = False
            for index, portname in enumerate(portsList):
                if "arduino" in portname.lower():
                    selectedIndex = index
                    
        else:
            portsList.append('None')
        
        size = wx.Size(150, 27)
        
        portText = wx.StaticText(self.panel, label="Port:")
        self.portBox = wx.ComboBox(self.panel, size=size, value=portsList[selectedIndex], choices=portsList)
        self.portBox.SetEditable(False)
        self.portBox.Select(selectedIndex)
        
        portSizer.Add(portText, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        portSizer.Add(self.portBox, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        
        self.baudRates = ["9600", "19200", "38400", "57600", "115200"]
        
        baudRateText = wx.StaticText(self.panel, label="Baud Rate:")
        self.baudRateBox = wx.ComboBox(self.panel, size=size, value=self.baudRates[4], choices=self.baudRates)
        self.baudRateBox.SetEditable(False)
        self.baudRateBox.Select(4)
        
        baudRateSizer.Add(baudRateText, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        baudRateSizer.Add(self.baudRateBox, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        
        patities = [serial.PARITY_NAMES[serial.PARITY_NONE], 
                        serial.PARITY_NAMES[serial.PARITY_EVEN],
                        serial.PARITY_NAMES[serial.PARITY_ODD],
                        serial.PARITY_NAMES[serial.PARITY_MARK],
                        serial.PARITY_NAMES[serial.PARITY_SPACE]]
        self.patitiesValues = [serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD, serial.PARITY_MARK, serial.PARITY_SPACE]
        
        parityText = wx.StaticText(self.panel, label="Parity:")
        self.parityBox = wx.ComboBox(self.panel, size=size, value=patities[0], choices=patities)
        self.parityBox.SetEditable(False)
        self.parityBox.Select(0)
        
        paritySizer.Add(parityText, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        paritySizer.Add(self.parityBox, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        
        stopBits = ["1", "1.5", "2"]
        self.stopBitsValues = [serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO]
        #STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO
        stopBitsText = wx.StaticText(self.panel, label="Stop Bits:")
        self.stopBitsBox = wx.ComboBox(self.panel, size=size, value=stopBits[0], choices=stopBits)
        self.stopBitsBox.SetEditable(False)
        self.stopBitsBox.Select(0)
        
        stopBitsSizer.Add(stopBitsText, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        stopBitsSizer.Add(self.stopBitsBox, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        
        flowControls = ["5 bits", "6 bits", "7 bits", "8 bits"]
        self.flowControlsValues = [serial.FIVEBITS, serial.SIXBITS, serial.SEVENBITS, serial.EIGHTBITS]
        #FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS
        flowControlText = wx.StaticText(self.panel, label="Flow Control:")
        self.flowControlBox = wx.ComboBox(self.panel, size=size, value=flowControls[0], choices=flowControls)
        self.flowControlBox.SetEditable(False)
        self.flowControlBox.Select(0)
        
        flowControlSizer.Add(flowControlText, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        flowControlSizer.Add(self.flowControlBox, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        
        btn = wx.Button(self.panel, label="Cancel")
        btn.Bind(wx.EVT_BUTTON, self.OnChancelPressed)
        buttonsSizer.Add(btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        btn = wx.Button(self.panel, label="Connect")
        btn.Bind(wx.EVT_BUTTON, self.OnConnectPressed)
        if connectDisabled:
            btn.Disable()
            
        buttonsSizer.Add(btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
  
        mainSizer.Add(portSizer, 0, wx.ALL|wx.ALIGN_RIGHT, 0)
        mainSizer.Add(baudRateSizer, 0, wx.ALL|wx.ALIGN_RIGHT, 0)
        mainSizer.Add(paritySizer, 0, wx.ALL|wx.ALIGN_RIGHT, 0)
        mainSizer.Add(stopBitsSizer, 0, wx.ALL|wx.ALIGN_RIGHT, 0)
        mainSizer.Add(flowControlSizer, 0, wx.ALL|wx.ALIGN_RIGHT, 0)
        mainSizer.Add(buttonsSizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
  
        self.panel.SetSizer(mainSizer)
        self.onConnect = None
        mainSizer.Layout()
        self.Bind(wx.EVT_CLOSE, self.OnChancelPressed)
    
    def setCB(self, onConnect):
        self.onConnect = onConnect
    
    def OnChancelPressed(self, event):
        self.parent.Enable(True)
        self.Hide()
        self.parent.SetFocus()
    
    def OnConnectPressed(self, event):
        port = self.portsValues[self.portBox.GetSelection()]
        baud = self.baudRates[self.baudRateBox.GetSelection()]
        parity = self.patitiesValues[self.parityBox.GetSelection()]
        stopBits = self.stopBitsValues[self.stopBitsBox.GetSelection()]
        flowControl = self.flowControlsValues[self.flowControlBox.GetSelection()]
        
        self.onConnect(port, baud, parity, stopBits, flowControl)
        self.parent.Enable(True)
        self.Hide()
        self.parent.SetFocus()
