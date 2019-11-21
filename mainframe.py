import wx
import sys
import os
from validatechannels import ValidateChannel
from model.model import Model, FILAMENT_CHANNEL, zipfolder
from model.agilentloop import DATA_DIR
from portsettings import PortSettings
from graphsettings import GraphSettings
from graph.canvas import Canvas
from matplotlib.figure import Figure
from model.profile import saveChToFile, loadChFromFile, saveFilamentToFile, loadFilamentFromFile
from model.agilentloop import agilentLoop, calculateLoop
from multiprocessing import Value
from threading import Thread
import sqlite3
from model.database import getCalculatedDataIndex, getGraphs, createTablesIfNotExists, getMipsData, remove
import config
# from progress import ProgressScreen


ID_SHOW_HIDE_GRAPH_MENU_BUTTON = 5
ID_ALWAYS_ON_TOP = 20
ID_SAVE_POSITION = 30
ID_SAVE_SIZE = 31
ID_CHANNELS_MENU = 32
ID_FILAMENT_MENU = 33

ID_NEW_CHANNELS = 100
ID_OPEN_CHANNELS = 101
ID_SAVE_CHANNELS = 102

ID_NEW_FILAMENT = 110
ID_OPEN_FILAMENT = 111
ID_SAVE_FILAMENT = 112

CHANNELS_NAMES = ('1', '2', '3', '4', '5', '6', '7', 'FB', 'Filament')

class GraphObject:
    def __init__(self):
        self.sumInt = []
        self.mass = 0
        self.color = "green"
        self.isLine = False
        self.value = 0
        self.channel = 0
        self.step = 0
        self.position = 0


class MainFrame(wx.Frame):

    def __init__(self, *args, **kw):
        # x_screen_center, y_screen__center = config.GetScreenCenter()
        # self.die = ProgressScreen(None, title='Process', size = wx.Size(400,320), pos = wx.Point(x_screen_center - 200, y_screen__center - 160),style = wx.STAY_ON_TOP)
        # self.die.Show()
        # pub.subscribe(self.appear, "show")
        # ensure the parent's __init__ is called
        super(MainFrame, self).__init__(*args, **kw)
        # sendUpdate()
        # icon = wx.Icon('bitmaps/icon.ico', wx.BITMAP_TYPE_ICO)
        icon = wx.Icon('bitmaps/app.ico', wx.BITMAP_TYPE_ICO)

        self.SetIcon(icon)
        self.graphShown = True

        self.alwaysOnTop,self.saveSize, self.savePosition, self.decreaseSize, self.expandSize = config.GetSavingConfig()

        self.db = sqlite3.connect('db.sqlite')
        createTablesIfNotExists(self.db)
        # remove(self.db)
        self.agilentRunning = False
        self.isConnectedToMIPS = False

        self.graphs = [{"mass": 1222, "color": "red"}]
        self.current_max_xlim = 1

        self.selectedChannel = 1

        self.model = Model(self.OnError, self.OnConnect, self.OnCantReconnect)
        # create a panel in the frame
        self.panel = wx.Panel(self)
         # create some sizers
        self.windowField = wx.BoxSizer(wx.VERTICAL)
        self.windowMainSizer = wx.BoxSizer(wx.HORIZONTAL)
        #  ---windowField---
        # |   canvasSizer   |
        # |                 |
        # |-----------------|
        # | windowMainSizer |
        #  -----------------
        windowMainSizerRight = wx.BoxSizer(wx.VERTICAL)
        windowMainSizerLeft = wx.BoxSizer(wx.VERTICAL)
        # sendUpdate()
        filament = wx.StaticBox(self.panel, label='')
        session = wx.StaticBox(self.panel, label="Session:")
        # control = wx.StaticBox(self.panel, label='')
        status = wx.StaticBox(self.panel, label="Status:")
        self.filamentSizer = wx.StaticBoxSizer(filament, wx.VERTICAL)
        self.sessionSizer = wx.StaticBoxSizer(session, wx.VERTICAL)
        self.controlSizer = wx.BoxSizer( wx.VERTICAL)
        statusSizer = wx.StaticBoxSizer(status, wx.VERTICAL)
        statusSizerH = wx.BoxSizer()

        self.controlSizer.AddSpacer(1)
        self.controlSizer.Add(wx.StaticText(self.panel, label='Control:'))
        # windowMainSizerRightBottom
        windowMainSizerRightBottom = wx.BoxSizer(wx.HORIZONTAL)

        connectionText = wx.StaticText(self.panel, label="Connection:")
        self.connectionBtn = wx.Button(self.panel, label='OFF', style=wx.NO_BORDER | wx.BU_EXACTFIT,
                                       size=wx.Size(23, 19))
        self.connectionBtn.SetBackgroundColour(wx.RED)
        self.connectionBtn.Bind(wx.EVT_BUTTON, self.onConnectionPressed)
        filamentText = wx.StaticText(self.panel, label="Filament:")
        self.filamentBtn = wx.Button(self.panel, label='OFF', style=wx.NO_BORDER | wx.BU_EXACTFIT, size=wx.Size(23, 19))
        self.filamentBtn.SetBackgroundColour(wx.RED)
        self.filamentBtn.Bind(wx.EVT_BUTTON, self.onFilamentPressed)
        # sendUpdate()
        statusSizerH.Add(connectionText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        statusSizerH.Add(self.connectionBtn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        statusSizerH.AddSpacer(20)
        statusSizerH.Add(filamentText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        statusSizerH.Add(self.filamentBtn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        figure = Figure(figsize=(2.5,4.4))
        # create the widgets
        self.canvas = Canvas(self.panel, -1, figure)

        self.graphSettingsButton = wx.Button(self.panel, label="Settings")
        self.graphSettingsButton.Bind(wx.EVT_BUTTON, self.onGraphSettingPressed)

        # SESSION BUTTONS
        sessionButton = wx.BoxSizer(wx.HORIZONTAL)
        backButton = wx.BitmapButton(self.panel, bitmap=wx.Bitmap("bitmaps/backward.png", wx.BITMAP_TYPE_ANY),
                                     style=wx.NO_BORDER | wx.BU_EXACTFIT)
        self.playButton = wx.BitmapButton(self.panel, bitmap=wx.Bitmap("bitmaps/play.png", wx.BITMAP_TYPE_ANY),
                                     style=wx.NO_BORDER | wx.BU_EXACTFIT)
        nextButton = wx.BitmapButton(self.panel, bitmap=wx.Bitmap("bitmaps/forward.png", wx.BITMAP_TYPE_ANY),
                                     style=wx.NO_BORDER | wx.BU_EXACTFIT)

        self.playButton.Bind(wx.EVT_BUTTON, self.onPlayPressed)
        sessionButton.Add(backButton, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 5)
        sessionButton.Add(self.playButton, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 5)
        sessionButton.Add(nextButton, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 5)
        # sendUpdate()
        # SESSION TYPE
        sessionBox = wx.ComboBox(self.panel, value="real-time", choices=["real-time", "Browse for past session"])
        sessionBox.SetEditable(False)

        # SLIDER
        slyderBox = wx.BoxSizer(wx.HORIZONTAL)
        self.minText = wx.StaticText(self.panel, label="-60", style=wx.TE_RIGHT)
        self.minText.SetMinSize((20,20))
        self.slider = wx.Slider(self.panel, value=10, minValue=-60, maxValue=60, size=wx.Size(800, 20),
                                style=wx.SL_SELRANGE)
        self.slider.SetCanFocus(False)
        self.slider.Bind(wx.EVT_SLIDER, self.onSliderScroll)
        self.maxText = wx.StaticText(self.panel, label="60")

        font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        slyderBox.AddSpacer(10)
        slyderBox.Add(self.minText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        slyderBox.Add(self.slider, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 3)
        slyderBox.Add(self.maxText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)

        # Mouse events on graph
        self.canvas.mpl_connect('motion_notify_event', self.onGraphMouseMove)
        position_static_text_field_move = wx.StaticText(self.panel, -1, 'Position(x):')
        self.position_text_field_move_x = wx.TextCtrl(self.panel, -1, '', size=(85, 25), style=wx.TE_READONLY | wx.TE_NO_VSCROLL)
        self.position_text_field_move_x.Enable(False)
        self.position_text_field_move_x.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        position_box_move = wx.BoxSizer(wx.VERTICAL)
        position_box_move.Add(position_static_text_field_move)
        position_box_move.Add(self.position_text_field_move_x)
        # sendUpdate()
        #
        self.canvas.mpl_connect('button_press_event', self.onGraphMouseButtonClick)
        position_static_text_field_click = wx.StaticText(self.panel, -1, 'Click position(x): ')
        self.position_text_field_click_x = wx.TextCtrl(self.panel, -1, '', size=(85, 25), style=wx.TE_READONLY)
        self.position_text_field_click_x.Enable(False)
        self.position_text_field_click_x.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        position_box_click = wx.BoxSizer(wx.VERTICAL)
        position_box_click.Add(position_static_text_field_click)
        position_box_click.Add(self.position_text_field_click_x)


        self.position_box = wx.BoxSizer(wx.VERTICAL)
        self.position_box.Add(position_box_move)
        self.position_box.AddSpacer(5)
        self.position_box.Add(position_box_click)

        self.right_canvas_box = wx.BoxSizer(wx.VERTICAL)
        self.right_canvas_box.Add(self.position_box, wx.ALIGN_CENTER | wx.ALIGN_RIGHT)
        self.right_canvas_box.AddSpacer(20)
        self.right_canvas_box.Add(self.graphSettingsButton, wx.ALIGN_BOTTOM)

        self.canvasSizer = wx.BoxSizer()
        self.canvasSizer.AddSpacer(6)
        self.canvasSizer.Add(self.canvas, 1, wx.ALIGN_LEFT)
        self.canvasSizer.AddSpacer(5)
        self.canvasSizer.Add(self.right_canvas_box, 0, wx.ALIGN_CENTER | wx.ALIGN_RIGHT)
        # sendUpdate()
        # CONTROLS
        channel = wx.StaticBox(self.panel, label='')
        controlsBox = wx.StaticBoxSizer(channel, wx.HORIZONTAL)

        # EDIT BUTTONS
        controlsBox.AddSpacer(2)
        values = ['1', '0.1', '0.01', '0.001']
        btnVBox = wx.BoxSizer(wx.VERTICAL)
        btnVBox.AddSpacer(19)

        for x in range(0, 2):
            sign = '-'
            if x == 0:
                sign = '+'

            btnHBox = wx.BoxSizer(wx.HORIZONTAL)
            for y in range(0, 4):
                btn = wx.Button(self.panel, label="%s%s" % (sign, values[y]), size=[45, 20])
                btn.SetFont(font)
                btn.Bind(wx.EVT_BUTTON, self.onIncrButtonPressed)
                btnHBox.Add(btn, 0, wx.ALL, 1)
            btnVBox.Add(btnHBox, 0, wx.ALL, 0)

        controlsBox.Add(btnVBox, 0, wx.ALL, 0)
        # sendUpdate()
        # ACTUAL AND SET VALUE
        valuesAndChannelsBox = wx.BoxSizer(wx.VERTICAL)
        # valuesAndChannelsBox.AddSpacer()
        self.channelButtons = []
        self.channelValues = []
        self.channelActualValues = []
        # CHANNELS BUTTONS
        channelsBox = wx.BoxSizer(wx.HORIZONTAL)
        selected = ''

        chSize = wx.Size(37, -1)

        # btn8 = self.createChannel(7)
        # print('')
        btn8 = wx.BitmapButton(self.panel, bitmap=wx.Bitmap("bitmaps/8.png", wx.BITMAP_TYPE_ANY),
                               style=wx.NO_BORDER | wx.BU_EXACTFIT)
        ch8Ctrl = wx.TextCtrl(self.panel, size=chSize, style=wx.TE_LEFT)
        ch8ActCtrl = wx.TextCtrl(self.panel, size=chSize, style=wx.TE_READONLY | wx.TE_LEFT)
        ch8ActCtrl.Enable(False)
        ch8ActCtrl.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        # sendUpdate()
        # btnF = wx.BitmapButton(self.panel, bitmap=wx.Bitmap("bitmaps/f.png", wx.BITMAP_TYPE_ANY),
        #                        style=wx.NO_BORDER | wx.BU_EXACTFIT)
        buttonBorderPanel = wx.Panel(self.panel, size=(65,17))
        buttonBorderPanelSizer = wx.BoxSizer()
        buttonBorderPanelVSizer = wx.BoxSizer(wx.VERTICAL)
        buttonBorderPanel.SetSizer(buttonBorderPanelSizer)
        buttonBorderPanel.SetBackgroundColour(wx.BLACK)
        buttonBackgroundPanel = wx.Panel(buttonBorderPanel, size=(63,15))
        text = wx.StaticText(buttonBackgroundPanel, label=CHANNELS_NAMES[8],size=(63,15), style=wx.TE_CENTRE)
        text.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL))

        buttonBackgroundPanel.SetBackgroundColour(wx.WHITE)
        buttonBorderPanelVSizer.AddSpacer(1)
        buttonBorderPanelVSizer.Add(buttonBackgroundPanel)
        buttonBorderPanelSizer.AddSpacer(1)
        buttonBorderPanelSizer.Add(buttonBorderPanelVSizer)

        self.filamentHeadSizer = wx.BoxSizer()
        self.filamentHeadSizer.Add(buttonBorderPanel)
        self.filamentHeadSizer.AddSpacer(10)
        self.filamentProfile = wx.StaticText(self.panel)
        self.filamentHeadSizer.Add(self.filamentProfile)
        self.filamentBottomSizer = wx.BoxSizer()
        # sendUpdate()
        text.Bind(wx.EVT_LEFT_DOWN, self.OnChannelPressed)
        # btnF.Bind(wx.EVT_BUTTON, self.OnChannelPressed)
        self.chFCtrlSizer = wx.BoxSizer(wx.HORIZONTAL)
        chFCtrl = wx.TextCtrl(self.panel, size=chSize, style=wx.TE_LEFT)
        chFCtrl.Bind(wx.EVT_TEXT, self.channelValueChanged)
        chFText = wx.StaticText(self.panel, label='Current (A)')
        self.chFCtrlSizer.Add(chFCtrl)
        self.chFCtrlSizer.AddSpacer(4)
        self.chFCtrlSizer.Add(chFText, 0 , wx.ALIGN_CENTER_VERTICAL)
        chFActCtrl = wx.TextCtrl(self.panel, size=chSize, style=wx.TE_READONLY | wx.TE_LEFT)
        chFActCtrl.Enable(False)
        chFActCtrl.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.channelButtons.append(buttonBackgroundPanel)
        # self.channelButtons.append(btnF)
        self.channelButtons.append(btn8)
        self.channelValues.append(chFCtrl)
        self.channelValues.append(ch8Ctrl)
        self.channelActualValues.append(chFActCtrl)
        self.channelActualValues.append(ch8ActCtrl)

        self.filamentControlSizer = wx.BoxSizer(wx.VERTICAL)
        # sendUpdate()
        self.voltageSizer = wx.BoxSizer(wx.HORIZONTAL)
        voltageText = wx.StaticText(self.panel, label="Voltage Drop (V)")
        self.voltageCtrl = wx.TextCtrl(self.panel, size=chSize, style=wx.TE_READONLY | wx.TE_LEFT)
        self.voltageCtrl.Enable(False)
        self.voltageCtrl.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Comic Sans MS'))
        self.voltageSizer.Add(self.voltageCtrl)
        self.voltageSizer.AddSpacer(4)
        self.voltageSizer.Add(voltageText, 0 , wx.ALIGN_CENTER_VERTICAL)
        self.emissionSizer = wx.BoxSizer(wx.HORIZONTAL)
        emissionText = wx.StaticText(self.panel, label="Emission (\u00B5A)")
        self.emissionCtrl = wx.TextCtrl(self.panel, size=chSize, style=wx.TE_READONLY | wx.TE_LEFT)
        self.emissionCtrl.Enable(False)
        self.emissionCtrl.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Comic Sans MS'))
        self.emissionSizer.Add(self.emissionCtrl)
        self.emissionSizer.AddSpacer(4)
        self.emissionSizer.Add(emissionText, 0 , wx.ALIGN_CENTER_VERTICAL)

        # self.filamentControlSizer.AddSpacer(3)
        # self.filamentControlSizer.Add(btnF)
        # self.filamentControlSizer.Add(self.filamentButtonSizer)
        self.filamentControlSizer.AddSpacer(5)
        self.filamentControlSizer.Add(self.chFCtrlSizer)
        self.filamentControlSizer.AddSpacer(3)
        self.filamentControlSizer.Add(chFActCtrl)
        self.filamentControlSizer.AddSpacer(3)
        self.filamentControlSizer.Add(self.voltageSizer)
        self.filamentControlSizer.AddSpacer(3)
        self.filamentControlSizer.Add(self.emissionSizer)
        self.filamentSizer.AddSpacer(3)
        self.filamentSizer.Add(self.filamentHeadSizer)
        self.filamentSizer.Add(self.filamentBottomSizer)
        self.filamentBottomSizer.Add(self.filamentControlSizer)
        # sendUpdate()

        valuesBox = wx.BoxSizer(wx.VERTICAL)

        channelText = wx.StaticText(self.panel, label="Channel:")
        setText = wx.StaticText(self.panel, label="Set:")
        realText = wx.StaticText(self.panel, label="Real:")
        valuesBox.Add(channelText)
        valuesBox.AddSpacer(10)
        valuesBox.Add(setText, 0, wx.ALIGN_RIGHT)
        valuesBox.AddSpacer(10)
        valuesBox.Add(realText, 0, wx.ALIGN_RIGHT)

        channelsBox.AddSpacer(3)
        channelsBox.Add(valuesBox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        # sendUpdate()
        for x in range(7, 0, -1):
            if x == 1:
                selected = 's'
            valuesBox = wx.BoxSizer(wx.VERTICAL)
            btn = wx.BitmapButton(self.panel, bitmap=wx.Bitmap("bitmaps/%d%s.png" % (x, selected), wx.BITMAP_TYPE_ANY),
                                  style=wx.NO_BORDER | wx.BU_EXACTFIT)
            btn.Bind(wx.EVT_BUTTON, self.OnChannelPressed)
            self.channelButtons.append(btn)
            valuesBox.Add(btn, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 0)
            valuesBox.AddSpacer(5)
            chCtrl = wx.TextCtrl(self.panel, size=chSize, style=wx.TE_LEFT)
            chCtrl.Bind(wx.EVT_TEXT, self.channelValueChanged)
            chActCtrl = wx.TextCtrl(self.panel, size=chSize, style=wx.TE_READONLY | wx.TE_LEFT)
            chActCtrl.Enable(False)
            chActCtrl.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            self.channelValues.append(chCtrl)
            self.channelActualValues.append(chActCtrl)
            valuesBox.Add(chCtrl, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 0)
            valuesBox.AddSpacer(3)
            valuesBox.Add(chActCtrl, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 0)
            channelsBox.Add(valuesBox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        # sendUpdate()
        valuesBox = wx.BoxSizer(wx.VERTICAL)
        btn8.Bind(wx.EVT_BUTTON, self.OnChannelPressed)
        valuesBox.Add(btn8, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 0)
        valuesBox.AddSpacer(5)
        valuesBox.Add(ch8Ctrl, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 0)
        valuesBox.AddSpacer(3)
        valuesBox.Add(ch8ActCtrl, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 0)
        channelsBox.Add(valuesBox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        ch8Ctrl.Bind(wx.EVT_TEXT, self.channelValueChanged)
        # sendUpdate()
        self.channelButtons.reverse()
        self.channelActualValues.reverse()
        self.channelValues.reverse()

        self.filamentTextBox = wx.BoxSizer(wx.VERTICAL)

        self.maxFText = wx.StaticText(self.panel, label="Max:")
        self.directionText = wx.StaticText(self.panel, label="Direction:")
        self.filamentTextBox.AddSpacer(55)
        self.filamentTextBox.Add(self.maxFText, 0, wx.ALIGN_RIGHT)
        self.filamentTextBox.AddSpacer(10)
        self.filamentTextBox.Add(self.directionText)
        # sendUpdate()
        self.filamentBottomSizer.Add(self.filamentTextBox, 0, wx.ALL, 5)

        # self.filamentSizer.Add(self.filamentTextBox, 0, wx.ALL, 5)

        self.filamentValueBox = wx.BoxSizer(wx.VERTICAL)
        self.filamentMaxCtrl = wx.TextCtrl(self.panel, size=(40, 18),
                                           style=wx.TE_CENTER | wx.TE_LEFT)  # , validator=ValidateChannel(self.maxFilamentChanged))
        self.filamentMaxCtrl.Bind(wx.EVT_TEXT, self.maxFilamentChanged)
        self.directionBtn = wx.Button(self.panel, label="FWD", size=[40, 20])
        self.directionBtn.Bind(wx.EVT_BUTTON, self.OnDirectionPressed)
        self.filamentValueBox.AddSpacer(54)
        self.filamentValueBox.Add(self.filamentMaxCtrl, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.filamentValueBox.AddSpacer(8)
        self.filamentValueBox.Add(self.directionBtn, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 0)

        self.filamentBottomSizer.Add(self.filamentValueBox, 0, wx.ALL, 5)

        # self.filamentSizer.Add(self.filamentValueBox, 0, wx.ALL, 5)

        chFont = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Comic Sans MS')
        for i in range(0, len(self.channelActualValues)):
            self.channelActualValues[i].SetFont(chFont)
            self.channelValues[i].SetFont(chFont)
        # sendUpdate()
        valuesAndChannelsBox.Add(channelsBox, 0, wx.ALL, 0)
        controlsBox.Add(valuesAndChannelsBox, 0, wx.ALL, 0)

        # Profile
        profile_box = wx.BoxSizer()
        profile_static_text_field = wx.StaticText(self.panel, label='Profile: ')
        self.profile_text_field = wx.StaticText(self.panel, label='Untitled')
        profile_box.Add(profile_static_text_field)
        profile_box.Add(self.profile_text_field)

        self.windowField.Add(profile_box, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.windowField.Hide(profile_box, recursive=True)
        self.windowField.Add(self.canvasSizer, 0, wx.EXPAND)
        self.windowField.Add(self.windowMainSizer)

        self.windowMainSizer.AddSpacer(5)
        self.windowMainSizer.Add(windowMainSizerLeft)
        self.windowMainSizer.AddSpacer(5)
        self.windowMainSizer.Add(windowMainSizerRight)
        # sendUpdate()
        windowMainSizerLeft.Add(self.sessionSizer)
        windowMainSizerRight.Add(self.controlSizer)
        windowMainSizerRight.Add(windowMainSizerRightBottom)

        self.sessionSizer.Add(sessionButton, 0, wx.ALL)
        self.sessionSizer.AddSpacer(5)
        self.sessionSizer.Add(sessionBox, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        self.sessionSizer.AddSpacer(5)

        self.controlSizer.Add(slyderBox, 0, wx.EXPAND)

        self.controls = wx.BoxSizer(wx.HORIZONTAL)
        self.controlsLeftSizer = wx.BoxSizer(wx.VERTICAL)
        self.controlsRightSizer = wx.BoxSizer(wx.VERTICAL)
        # sendUpdate()
        self.controls.Add(self.controlsLeftSizer)
        self.controls.AddSpacer(5)
        self.controls.Add(self.controlsRightSizer)

        self.controlsLeftSizer.Add(controlsBox)
        self.controlsLeftSizer.Add(statusSizer)
        statusSizer.Add(statusSizerH)
        statusSizer.AddSpacer(4)
        self.controlsRightSizer.Add(self.filamentSizer)

        self.controlSizer.Add(self.controls)


        self.panel.SetSizer(self.windowField)

        if self.graphShown:
            self.graphShown = False
            self.windowMainSizer.Hide(self.sessionSizer, recursive=True)
            self.windowField.Hide(self.canvasSizer, recursive=True)
            # (890, 250)
            size = wx.Size(self.decreaseSize)
            self.SetMinSize(wx.Size(config.decreaseSize))
            self.SetSize(size)
        # sendUpdate()
        self.model.connect()
        self.currentChannel = 0
        self.selectChannel(self.currentChannel)
        self.makeMenuBar()
        self.updateSetValues()
        # sendUpdate()

    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        self.fileMenu = wx.Menu()
        # newProfile = self.fileMenu.Append(wx.ID_NEW, '&New Profile')
        # self.fileMenu.AppendSeparator()
        self.chMenu = wx.Menu()
        self.filamentMenu = wx.Menu()
        self.fileMenu.AppendSubMenu(self.chMenu, '&Channels Profile')
        self.fileMenu.AppendSubMenu(self.filamentMenu, '&Filament Profile')

        # When using a stock ID we don't need to specify the menu item's
        #

        # loadChProfile = self.chMenu.Append(ID_OPEN_CHANNELS, '&Load')
        loadChProfile = wx.MenuItem(self.fileMenu, ID_OPEN_CHANNELS, '&Load')
        loadChProfile.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, (16,16)))
        # saveChProfile = self.chMenu.Append(ID_SAVE_CHANNELS, '&Save')
        saveChProfile = wx.MenuItem(self.fileMenu, ID_SAVE_CHANNELS, '&Save')
        saveChProfile.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_OTHER, (16,16)))

        self.chMenu.Append(loadChProfile)
        self.chMenu.Append(saveChProfile)

        #
        # loadFilamentProfile = self.filamentMenu.Append(ID_OPEN_FILAMENT, '&Load')
        loadFilamentProfile = wx.MenuItem(self.fileMenu, ID_OPEN_FILAMENT, '&Load')
        loadFilamentProfile.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, (16,16)))
        # saveFilamentProfile = self.filamentMenu.Append(ID_SAVE_FILAMENT, '&Save')
        saveFilamentProfile = wx.MenuItem(self.fileMenu, ID_SAVE_FILAMENT, '&Save')
        saveFilamentProfile.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_OTHER, (16,16)))

        self.filamentMenu.Append(loadFilamentProfile)
        self.filamentMenu.Append(saveFilamentProfile)

        quit_button = wx.MenuItem(self.fileMenu, wx.ID_EXIT, '&Quit\tCtrl+Q')
        quit_button.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_OTHER, (16,16)))
        self.fileMenu.AppendSeparator()
        self.fileMenu.Append(quit_button)
        # self.Bind(wx.EVT_MENU, self.onNewProfile, newProfile)
        self.Bind(wx.EVT_MENU, self.onLoadChProfile, loadChProfile)
        self.Bind(wx.EVT_MENU, self.onSaveChProfile, saveChProfile)
        self.Bind(wx.EVT_MENU, self.onLoadFilamentProfile, loadFilamentProfile)
        self.Bind(wx.EVT_MENU, self.onSaveFilamentProfile, saveFilamentProfile)
        self.Bind(wx.EVT_MENU, self.OnExit, quit_button)
        # Make a view menu

        self.view_menu = wx.Menu()
        # self.view_menu.AppendSeparator()
        self.view_menu.AppendCheckItem(ID_ALWAYS_ON_TOP, '&Always on top')
        self.view_menu.Check(ID_ALWAYS_ON_TOP, self.alwaysOnTop)
        self.view_menu.AppendSeparator()
        self.view_menu.AppendCheckItem(ID_SAVE_POSITION, '&Save Position')
        self.view_menu.Check(ID_SAVE_POSITION, self.savePosition)
        self.view_menu.AppendCheckItem(ID_SAVE_SIZE, '&Save Size')
        self.view_menu.Check(ID_SAVE_SIZE, self.saveSize)
        # self.view_menu.AppendSeparator()

        # showHideGraph = self.view_menu.Append(ID_SHOW_HIDE_GRAPH_MENU_BUTTON, '&Show Graph')


        self.Bind(wx.EVT_MENU, self.onAlwaysOnTop, id=ID_ALWAYS_ON_TOP)
        # self.Bind(wx.EVT_MENU, self.onShowHideGraph, showHideGraph)
        self.Bind(wx.EVT_MENU, self.onSavePosition, id=ID_SAVE_POSITION)
        self.Bind(wx.EVT_MENU, self.onSaveSize, id=ID_SAVE_SIZE)
        # Make a about menu

        self.about_menu = wx.Menu()
        # self.about_menu.AppendSeparator()
        version = self.about_menu.Append(wx.ID_ABOUT, '&Version')

        self.Bind(wx.EVT_MENU, self.onVersion, version)
        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(self.fileMenu, "&File")
        self.menuBar.Append(self.view_menu, "&View")
        self.menuBar.Append(self.about_menu, "&About")

        # Give the menu bar to the frame
        self.SetMenuBar(self.menuBar)

        self.Bind(wx.EVT_CLOSE, self.OnExit)

    def OnExit(self, event):
        if self.model.appData.getConnectionControlValue() == 1:
            self.model.appData.setConnectionControlValue(0)
        if self.agilentRunning:
            self.agilentRunning = False

        config.SavingUsersConfig(window=self)
        sys.exit()

    def onPlayPressed(self, event):
        if self.agilentRunning:
            self.agilentRunning = False
            self.playButton.SetBitmapLabel(bitmap=wx.Bitmap('bitmaps/play.png', wx.BITMAP_TYPE_ANY))
            with self.agilentControlValue.get_lock():
                self.agilentControlValue.value = 0
            # save session
            path = os.path.join(os.getcwd(), DATA_DIR)
            zipfolder(DATA_DIR, path)
        else:
            self.agilentRunning = True
            self.playButton.SetBitmapLabel(bitmap = wx.Bitmap('bitmaps/stop.png', wx.BITMAP_TYPE_ANY))
            self.agilentControlValue = Value('i', 1)
            self.agilentProcess = Thread(target=agilentLoop, args=(self.agilentControlValue,))
            self.agilentProcess.daemon = True
            self.agilentProcess.start()
            self.calcProcess = Thread(target=calculateLoop, args=(self.agilentControlValue,))
            self.calcProcess.daemon = True
            self.calcProcess.start()
            wx.CallLater(1000, self.updateGraphs)

    def onNewProfile(self, event):
        self.updateChannelUI()
        profile_name = "Untitled"
        self.SetTitle(config.APP_NAME + ' - ' + profile_name)
        self.profile_text_field.SetLabel(profile_name)
        self.panel.Layout()

    def onLoadChProfile(self, event):
        openFileDialog = wx.FileDialog(self, "Open", "", "",
                                       "Profile files (*.pro)|*.pro",
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        path = os.path.join(os.getcwd(), "profiles")
        if not os.path.exists(path):
            os.makedirs(path)
        openFileDialog.SetDirectory(path)
        answer = openFileDialog.ShowModal()
        if answer == wx.ID_CANCEL:
            return
        if len(openFileDialog.GetPath()) > 0:
            answer = loadChFromFile(openFileDialog.GetPath(), self.model.appData, self.model)
            if answer == wx.ID_CANCEL:
                return
            profile_name = os.path.basename(openFileDialog.GetPath()).replace('.pro', '')
            self.SetTitle(config.APP_NAME + ' - ' + profile_name)
            self.profile_text_field.SetLabel(profile_name)
            self.panel.Layout()
        openFileDialog.Destroy()

        self.updateChannelUI()
        # self.model.appData.setFilamentStatus(0)
        for i in range(0, len(self.channelButtons)):
            self.channelValues[i].SetValue(str(self.model.getChannelValue(i)))
        self.updateDeviceUI()
        self.updateSetValues()

    def onSaveChProfile(self, event):
        saveFileDialog = wx.FileDialog(self, "Save As", "", "",
                                       "Profile files (*.pro)|*.pro",
                                       wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        path = os.path.join(os.getcwd(), "profiles")
        if not os.path.exists(path):
            os.makedirs(path)
        saveFileDialog.SetDirectory(path)
        answer = saveFileDialog.ShowModal()
        if answer == wx.ID_CANCEL:
            return
        if len(saveFileDialog.GetPath()) > 0:
            saveChToFile(saveFileDialog.GetPath(), self.model.appData)
            profile_name = os.path.basename(saveFileDialog.GetPath()).replace('.pro', '')
        saveFileDialog.Destroy()

        self.SetTitle(config.APP_NAME + ' - ' + profile_name)
        self.profile_text_field.SetLabel(profile_name)
        self.panel.Layout()

    def onLoadFilamentProfile(self, event):
        openFileDialog = wx.FileDialog(self, "Open", "", "",
                                       "Profile files (*.fpro)|*.fpro",
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        path = os.path.join(os.getcwd(), "profiles")
        if not os.path.exists(path):
            os.makedirs(path)
        openFileDialog.SetDirectory(path)
        answer = openFileDialog.ShowModal()
        if answer == wx.ID_CANCEL:
            return
        if len(openFileDialog.GetPath()) > 0:
            loadFilamentFromFile(openFileDialog.GetPath(), self.model.appData)
            profile_name = os.path.basename(openFileDialog.GetPath()).replace('.fpro', '')
            self.filamentProfile.SetLabel(': '  + profile_name)
            # self.profile_text_field.SetLabel(profile_name)
            self.panel.Layout()
        openFileDialog.Destroy()

        self.updateChannelUI()
        # self.model.appData.setFilamentStatus(0)
        # if self.model.isFilamentOn():
        #     self.model.appData.setFilamentStatus(1)
        # else:
        #     self.model.appData.setFilamentStatus(0)
        for i in range(0, len(self.channelButtons)):
            self.channelValues[i].SetValue(str(self.model.getChannelValue(i)))
        self.updateDeviceUI()
        self.updateSetValues()
        self.filamentMaxCtrl.SetLabel('')


    def onSaveFilamentProfile(self, event):
        saveFileDialog = wx.FileDialog(self, "Save As", "", "",
                                       "Profile files (*.fpro)|*.fpro",
                                       wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        path = os.path.join(os.getcwd(), "profiles")
        if not os.path.exists(path):
            os.makedirs(path)
        saveFileDialog.SetDirectory(path)
        answer = saveFileDialog.ShowModal()
        if answer == wx.ID_CANCEL:
            return
        if len(saveFileDialog.GetPath()) > 0:
            if self.model.isFilamentOn():
                filamentStatus = 1
            else:
                filamentStatus = 0
            saveFilamentToFile(saveFileDialog.GetPath(), self.model.appData, filamentStatus)
        saveFileDialog.Destroy()
        self.panel.Layout()

    def onAlwaysOnTop(self, event):
        if self.view_menu.IsChecked(event.GetId()):
            self.SetWindowStyle(config.onTopTrue)
            self.alwaysOnTop = True
        else:
            self.SetWindowStyle(config.onTopFalse)
            self.alwaysOnTop = False

    def onSavePosition(self, event):
        if self.view_menu.IsChecked(ID_SAVE_POSITION) == True:
            self.savePosition = True
        else:
            self.savePosition = False

    def onSaveSize(self, event):
        if self.view_menu.IsChecked(ID_SAVE_SIZE) == True:
            self.saveSize = True
        else:
            self.saveSize = False

    def onVersion(self, event):
        message = '\nDate: %s\n\nVersion: %s' % (config.date, config.version)
        wx.MessageBox(message, 'Version', wx.OK | wx.ICON_ASTERISK)

    def onShowHideGraph(self, event):
        if self.graphShown:
            self.expandSize = self.GetSize()
            self.menuBar.SetLabel(ID_SHOW_HIDE_GRAPH_MENU_BUTTON, '&Show Graph')
            self.graphShown = False
            self.windowMainSizer.Hide(self.sessionSizer, recursive=True)
            self.windowField.Hide(self.canvasSizer, recursive=True)
            # (890, 250)
            size = wx.Size(self.decreaseSize)
            self.SetMinSize(wx.Size(config.decreaseSize))
            self.SetSize(size)
        else:
            self.decreaseSize = self.GetSize()
            self.menuBar.SetLabel(ID_SHOW_HIDE_GRAPH_MENU_BUTTON, '&Hide Graph')
            self.graphShown = True
            self.windowMainSizer.Show(self.sessionSizer, recursive=True)
            self.windowField.Show(self.canvasSizer, recursive=True)
            size = wx.Size(self.expandSize)
            self.SetMinSize(wx.Size(config.expandSize))
            self.SetSize(size)
            self.Refresh()

    def onGraphMouseMove(self, event):
        if (self.canvas.axis.in_axes(event)):
            x_descartes = self.canvas.axis.transData.inverted().transform((event.x, event.y))[0]
            if x_descartes < 0 or x_descartes > self.current_max_xlim:
                self.position_text_field_move_x.SetValue('0')
            else:
                self.position_text_field_move_x.SetValue('%.2f' % x_descartes)
        else:
            self.position_text_field_move_x.SetValue('0')

    def onGraphMouseButtonClick(self, event):
        if (self.canvas.axis.in_axes(event)):
            x_descartes = self.canvas.axis.transData.inverted().transform((event.x, event.y))[0]
            if x_descartes < 0 or x_descartes > self.current_max_xlim:
                self.position_text_field_click_x.SetValue('0')
            else:
                self.position_text_field_click_x.SetValue('%.3f' % x_descartes)
        else:
            self.position_text_field_click_x.SetValue('0')

    def OnChannelPressed(self, event):
        for i, val in enumerate(self.channelButtons):
            if val == event.GetEventObject():
                self.selectChannel(i)
            elif type(val) == type(wx.Panel()) and type(wx.StaticText()) == type(event.GetEventObject()):
                self.selectChannel(i)

    def onIncrButtonPressed(self, event):
        strVal = event.GetEventObject().GetLabel()
        flVal = float(strVal)
        self.setChannelValue(flVal)

    def setChannelValue(self, value):
        maxVal = float(self.model.getMaxValue(self.selectedChannel))
        minVal = float(self.model.getMinValue(self.selectedChannel))
        val = self.model.getChannelValue(self.selectedChannel)
        val = val + value
        if val > maxVal:
            val = maxVal
        if val < minVal:
            val = minVal
        self.model.setChannelValue(self.selectedChannel, val)
        self.channelValues[self.selectedChannel].SetValue(str(val))
        self.updateChannelUI()

    def selectChannel(self, channel):
        if self.currentChannel == FILAMENT_CHANNEL:
            # self.channelButtons[self.currentChannel].SetBitmapLabel(wx.Bitmap("bitmaps/f.png"))
            self.channelButtons[self.currentChannel].SetBackgroundColour(wx.WHITE)
            self.channelButtons[self.currentChannel].Refresh()
        else:
            self.channelButtons[self.currentChannel].SetBitmapLabel(wx.Bitmap("bitmaps/%d.png" % (self.currentChannel + 1)))
        for i in range(len(self.channelButtons)):
            if i == channel:
                if i == FILAMENT_CHANNEL:
                    # self.channelButtons[i].SetBitmapLabel(wx.Bitmap("bitmaps/fs.png"))
                    self.channelButtons[i].SetBackgroundColour(config.channelColour)
                    self.channelButtons[i].Refresh()
                else:
                    self.channelButtons[i].SetBitmapLabel(wx.Bitmap("bitmaps/%ds.png" % (i + 1)))
        self.currentChannel = channel
        self.selectedChannel = channel
        # maxVal = self.model.getMaxValue(self.selectedChannel)
        # minVal = self.model.getMinValue(self.selectedChannel)
        # if self.currentChannel == FILAMENT_CHANNEL:
        #     self.slider.SetTickFreq((abs(minVal)+abs(maxVal))*10)
        #     print((abs(minVal)+abs(maxVal))*10)
        # else:
        #     self.slider.SetTickFreq((abs(minVal) + abs(maxVal)) * 10)
        #     print((abs(minVal)+abs(maxVal))*10)
        self.updateChannelUI()

    def onSpin(self, event):
        pos = event.GetPosition()
        self.model.appData.setFilamentMaxCurrent(pos)
        self.updateChannelUI()

    def onSliderScroll(self, e):
        self.slider.SetCanFocus(False)
        obj = e.GetEventObject()
        val = obj.GetValue()
        self.model.setChannelValue(self.selectedChannel, float(val) / self.sliderMultiplier())
        self.channelValues[self.selectedChannel].SetValue(str(float(val) / self.sliderMultiplier()))
        if self.slider.GetValue() > 0:
            self.slider.SetSelection(0, self.slider.GetValue())
        else:
            self.slider.SetSelection(self.slider.GetValue(),0)

    def maxFilamentChanged(self, event):
        text = self.filamentMaxCtrl.GetValue()
        if text != '':
            try:
                val = float(text)
                self.model.appData.setFilamentMaxCurrent(val)
                self.updateChannelUI()
            except:
                e = sys.exc_info()[0]
                print(e)

    def channelValueChanged(self, event):
        # print(event)
        for i, val in enumerate(self.channelValues):
            if val == event.GetEventObject():
                try:
                    # if val.GetValue() == '':
                    #     self.slider.SetSelection(0,0)
                    #     return
                    flVal = float(val.GetValue())
                    if i == FILAMENT_CHANNEL:
                        if flVal < 0:
                            raise
                        if flVal > self.model.appData.getFilamentMaxCurrent():
                            raise
                    else:
                        if flVal > self.model.deviceData.getChannelsMaxValues(i):
                            raise
                        if flVal < self.model.deviceData.getChannelsMinValues(i):
                            raise
                        # return
                except:
                    if i == FILAMENT_CHANNEL:
                        val.SetValue(str(self.model.appData.getFilamentCurrent()))
                    else:
                        # val.SetValue(str(self.model.deviceData.getChannelsMaxValues(i)))
                        val.SetValue(str(self.model.appData.getChannelValue(i)))
                    return

                self.model.setChannelValue(i, float(val.GetValue()))
                if self.selectedChannel == i:
                    valCalc = int(self.model.getChannelValue(self.selectedChannel) * self.sliderMultiplier())
                    if self.slider.GetValue() != valCalc:
                        self.slider.SetValue(valCalc)
                        val = self.model.getRealValue(self.selectedChannel)
                        if val > self.slider.GetValue():
                            self.slider.SetSelection(self.slider.GetValue(), int(val * self.sliderMultiplier()))
                        else:
                            self.slider.SetSelection(int(val * self.sliderMultiplier()), self.slider.GetValue())

    def updateChannelUI(self):
        maxVal = self.model.getMaxValue(self.selectedChannel)
        minVal = self.model.getMinValue(self.selectedChannel)
        val = self.model.getRealValue(self.selectedChannel)
        self.minText.SetLabel(str(minVal))
        self.maxText.SetLabel(str(maxVal))
        self.slider.SetMax(int(maxVal * self.sliderMultiplier()))
        self.slider.SetMin(int(minVal * self.sliderMultiplier()))
        self.slider.SetValue(int(self.model.getChannelValue(self.selectedChannel) * self.sliderMultiplier()))
        if val > self.slider.GetValue():
            self.slider.SetSelection(self.slider.GetValue(), int(val * self.sliderMultiplier()))
        else:
            self.slider.SetSelection(int(val * self.sliderMultiplier()), self.slider.GetValue())

    def updateDeviceUI(self):
        val = self.model.getRealValue(self.selectedChannel)
        if val > self.slider.GetValue():
            self.slider.SetSelection(self.slider.GetValue(), int(val * self.sliderMultiplier()))
        else:
            self.slider.SetSelection(int(val * self.sliderMultiplier()), self.slider.GetValue())
        emission = self.model.getEmission()
        self.emissionCtrl.SetValue(str(emission))
        voltage = self.model.getFilamentVoltage()
        self.voltageCtrl.SetValue(str(voltage))

        for i in range(0, len(self.channelButtons)):
            self.channelActualValues[i].SetValue(str(self.model.getRealValue(i)))
        #    self.channelValues[i].SetValue(str(self.model.getChannelValue(i)))

        if not self.model.isFilamentOn():
            self.filamentBtn.SetLabel('OFF')
            self.filamentBtn.SetBackgroundColour(wx.RED)
        else:
            self.filamentBtn.SetLabel('ON')
            self.filamentBtn.SetBackgroundColour(wx.GREEN)

        if self.model.isDirectionFwd():
            self.directionBtn.SetLabel("FWD")
        else:
            self.directionBtn.SetLabel("REV")

    def updateSetValues(self):
        for i in range(0, len(self.channelButtons)):
            self.channelValues[i].SetValue(str(self.model.getChannelValue(i)))

    def connectWithParams(self, port, baudRate, parity, stopBits, flowControl):
        self.model.connectWithParams(port, baudRate, parity, stopBits, flowControl)

    def OnError(self, message):
        print("error")
        print(message)
        self.connectionBtn.SetLabel('OFF')
        self.connectionBtn.SetBackgroundColour(wx.RED)
        self.isConnectedToMIPS = False

    def OnConnect(self):
        self.connectionBtn.SetLabel('ON')
        self.connectionBtn.SetBackgroundColour(wx.GREEN)
        self.updateUI()
        self.isConnectedToMIPS = True

    def OnCantReconnect(self):
        if not self.IsShown():
            wx.CallLater(500, self.OnCantReconnect)
        else:
            self.connectionBtn.SetLabel('OFF')
            self.connectionBtn.SetBackgroundColour(wx.RED)
            frame = PortSettings(parent=self)
            frame.setCB(self.connectWithParams)
            size = wx.Size(config.portSettingsSize)
            frame.Show()
            frame.SetSize(size)
            self.isConnectedToMIPS = False

    def OnDirectionPressed(self, event):
        self.model.directionTrigger()

    def onGraphSettingPressed(self, event):
        frame = GraphSettings(parent=self)
        size = wx.Size(config.grapgSettingsSize)
        frame.Show()
        frame.SetSize(size)

    def updateGraphs(self):
        if self.agilentRunning == False:
            return
        graphs = getGraphs(self.db)

        maxStep = 0
        objs = []
        for gr in graphs:
            obj = GraphObject()
            obj.mass = gr[1]
            obj.color = gr[2]
            obj.position = gr[3]
            obj.sumInt = getCalculatedDataIndex(self.db, gr[0])
            if maxStep < len(obj.sumInt):
                maxStep = len(obj.sumInt)
            objs.append(obj)

        lines = getMipsData(self.db, maxStep)
        for line in lines:
            obj = GraphObject()
            obj.isLine = True
            obj.value = line[1]
            obj.step = line[0]
            obj.channel = line[2]
            objs.append(obj)

        self.current_max_xlim = self.canvas.redraw(objs)
        wx.CallLater(1000, self.updateGraphs)

    #     def RedrawGraph(self, graphs):
    #         self.graphs = graphs
    #         self.canvas.prepareGraph(self.graphs)
    #         self.canvas.redraw()
    #         self.canvasZoom.prepareGraph(self.graphs)
    #         self.canvasZoom.redraw()

    def updateUI(self):
        if self.model.appData.getConnectionControlValue() == 0:
            if self.isConnectedToMIPS:
                self.connectionBtn.SetLabel('OFF')
                self.connectionBtn.SetBackgroundColour(wx.RED)
                self.isConnectedToMIPS = False
        else:
            if not self.isConnectedToMIPS:
                self.connectionBtn.SetLabel('ON')
                self.connectionBtn.SetBackgroundColour(wx.GREEN)
                self.isConnectedToMIPS = True
        self.updateDeviceUI()
        wx.CallLater(50, self.updateUI)

    def sliderMultiplier(self):
        if self.selectedChannel == FILAMENT_CHANNEL:
            return 100
        return 10

    def onConnectionPressed(self, event):
        if self.model.appData.getConnectionControlValue() == 0:
            frame = PortSettings(parent=self)
            frame.setCB(self.connectWithParams)
            size = wx.Size(config.portSettingsSize)
            frame.Show()
            frame.SetSize(size)
        else:
            self.connectionBtn.SetLabel('OFF')
            self.connectionBtn.SetBackgroundColour(wx.RED)
            self.model.appData.setConnectionControlValue(0)
            self.isConnectedToMIPS = False

    def onFilamentPressed(self, event):
        self.model.filamentTrigger()

    # def appear(self):
    #     self.die.Destroy()
    #     self.Show()

    # def createChannel(self, channel):
    #     buttonBorderPanel = wx.Panel(self.panel, size=(37, 17))
    #     buttonBorderPanelSizer = wx.BoxSizer()
    #     buttonBorderPanelVSizer = wx.BoxSizer(wx.VERTICAL)
    #     buttonBorderPanel.SetSizer(buttonBorderPanelSizer)
    #     buttonBorderPanel.SetBackgroundColour(wx.BLACK)
    #     buttonBackgroundPanel = wx.Panel(buttonBorderPanel, size=(35, 15))
    #     text = wx.StaticText(buttonBackgroundPanel, label=CHANNELS_NAMES[channel], size=(35, 15), style=wx.TE_CENTRE)
    #     text.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
    #
    #     buttonBackgroundPanel.SetBackgroundColour(wx.WHITE)
    #     buttonBorderPanelVSizer.AddSpacer(1)
    #     buttonBorderPanelVSizer.Add(buttonBackgroundPanel)
    #     buttonBorderPanelSizer.AddSpacer(1)
    #     buttonBorderPanelSizer.Add(buttonBorderPanelVSizer)
    #     text.Bind(wx.EVT_LEFT_DOWN, self.OnChannelPressed)
    #     print('here')
    #     return buttonBackgroundPanel

# from wx.lib.pubsub import pub
# def sendUpdate():
#     pub.sendMessage('update', msg='sended')

