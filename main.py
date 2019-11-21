import wx
from mainframe import MainFrame
import multiprocessing
from config import GetConfigurations, APP_NAME

if __name__ == '__main__':

    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    multiprocessing.freeze_support()
    app = wx.App()
    pos, size, style = GetConfigurations()
    frm = MainFrame(None, title=APP_NAME +' - Untitled', size=size, pos=pos, style=style)
    frm.Show()
    app.MainLoop()