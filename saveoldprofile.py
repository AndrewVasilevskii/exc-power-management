import wx
import sqlite3
from model.database import insertMode

ID_MODE_OFF_MENU_BUTTON = 10
ID_MODE_ECD_MENU_BUTTON = 11
ID_MODE_STANDBY_MENU_BUTTON = 12
ID_MODE_TRANSMISSION_MENU_BUTTON = 13

class SaveOldProfileFrame(wx.Frame):

    def __init__(self, profile_name):
        # ensure the parent's __init__ is called
        size = wx.Size(280, 150)
        wx.Frame.__init__(self, None, title="Operating mode", size=size)
        self.SetMinSize(size)
        self.panel = wx.Panel(self)
        self.db = sqlite3.connect('db.sqlite')
        self.modes = {'Off': ID_MODE_OFF_MENU_BUTTON, 'ECD': ID_MODE_ECD_MENU_BUTTON, 'Standby': ID_MODE_STANDBY_MENU_BUTTON,
                      'Transmission': ID_MODE_TRANSMISSION_MENU_BUTTON}
        self.profile_name = profile_name
        self.selectedMode = ID_MODE_OFF_MENU_BUTTON
        self.windowField = wx.BoxSizer(wx.VERTICAL)
        self.modeChoiseSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.accept_cancel = wx.BoxSizer(wx.HORIZONTAL)

        noProfileText = 'No mode selected for profile: \'%s\'. Select it.\n' % (self.profile_name)
        self.noProfileTextField = wx.StaticText(self.panel,label=noProfileText)

        self.offModeButton = wx.RadioButton(self.panel, label='Off')
        self.ecdModeButton = wx.RadioButton(self.panel, label='ECD')
        self.standbyModeButton = wx.RadioButton(self.panel, label='Standby')
        self.transmissionModeButton = wx.RadioButton(self.panel, label='Transmission')
        self.offModeButton.Bind(wx.EVT_RADIOBUTTON, self.onModePressed)
        self.ecdModeButton.Bind(wx.EVT_RADIOBUTTON, self.onModePressed)
        self.standbyModeButton.Bind(wx.EVT_RADIOBUTTON, self.onModePressed)
        self.transmissionModeButton.Bind(wx.EVT_RADIOBUTTON, self.onModePressed)

        self.acceptButton = wx.Button(self.panel, label='Accept', size=(50,30))
        self.acceptButton.Bind(wx.EVT_BUTTON, self.onAcceptButton)
        self.cancelButton = wx.Button(self.panel, label='Cancel', size=(50,30))
        self.cancelButton.Bind(wx.EVT_BUTTON, self.onCancelButton)


        self.windowField.AddSpacer(10)
        self.windowField.Add(self.noProfileTextField, 0, wx.ALIGN_CENTER_HORIZONTAL, 4)
        self.windowField.Add(self.modeChoiseSizer,wx.ALIGN_CENTER_HORIZONTAL,5)
        self.windowField.Add(self.accept_cancel, 0, wx.ALIGN_CENTER_HORIZONTAL,5)
        self.windowField.AddSpacer(10)

        self.modeChoiseSizer.Add(self.offModeButton)
        self.modeChoiseSizer.Add(self.ecdModeButton)
        self.modeChoiseSizer.Add(self.standbyModeButton)
        self.modeChoiseSizer.Add(self.transmissionModeButton)

        self.accept_cancel.Add(self.acceptButton)
        self.accept_cancel.AddSpacer(15)
        self.accept_cancel.Add(self.cancelButton)

        self.panel.SetSizer(self.windowField)

        self.Bind(wx.EVT_CLOSE, self.onExit)

    def onExit(self, event):
        self.selectedMode = 0
        insertMode(self.db, self.selectedMode)
        self.Hide()

    def onAcceptButton(self, event):
        insertMode(self.db, self.selectedMode)
        self.Hide()

    def onCancelButton(self, event):
        self.selectedMode = 0
        insertMode(self.db, self.selectedMode)
        self.Hide()

    def onModePressed(self, event):
        self.selectedMode = self.modes[event.GetEventObject().GetLabel()]
