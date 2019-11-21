import wx
import sqlite3


class ErrorFrame(wx.Frame):

    def __init__(self):
        # ensure the parent's __init__ is called
        size = wx.Size(700, 300)
        wx.Frame.__init__(self, None, title="Error", style=wx.ALL, size=size)
        self.SetMinSize(size)
        self.panel = wx.Panel(self)