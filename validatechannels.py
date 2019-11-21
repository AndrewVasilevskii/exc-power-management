import wx

class ValidateChannel(wx.Validator):
    def __init__ (self, textChanged):
        wx.Validator.__init__(self)
        self.textChanged = textChanged
        self.Bind(wx.EVT_TEXT, self.On_Text_Change)
    def Clone(self):
        return ValidateChannel(self.textChanged)
    def On_Text_Change(self, event):
        self.textChanged()
        event.Skip()