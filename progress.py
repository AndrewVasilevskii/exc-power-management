
import wx
from wx.lib.pubsub import pub
import queue
import threading
import time

class ProgressScreen(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(ProgressScreen, self).__init__(*args, **kwargs)
        self.count = 0
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.progress = wx.Gauge(self, size=(250,10), pos=(75,250),range=20)
        self.queue = queue.Queue()
        pub.subscribe(self.updateProgress, "update")
        update = threading.Thread(target=self.update)
        update.daemon=True
        update.start()

    def OnEraseBackground(self, evt):
        dc = evt.GetDC()
        # if not dc:
        #     dc = wx.ClientDC(self)
        #     rect = self.GetUpdateRegion().GetBox()
        #     dc.SetClippingRect(rect)
        # dc.Clear()
        bmp = wx.Bitmap((wx.Bitmap('bitmaps/emblem.png').ConvertToImage()).Scale(400, 320, wx.IMAGE_QUALITY_HIGH))
        dc.DrawBitmap(bmp, 0, 0)
    #----------------------------------------------------------------------
    def updateProgress(self, msg):
        self.queue.put(msg)

    def update(self):
        proc = True
        while proc:
            if not self.count == 20:
                if not self.queue.empty():
                    self.queue.get()
                    self.count += 1
                    self.progress.SetValue(self.count)
                    self.Layout()
            else:
                if self.queue.empty():
                    time.sleep(0.2)
                    proc = False
                    pub.sendMessage("show")
            time.sleep(0.02)