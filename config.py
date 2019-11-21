
APP_NAME = 'ExDPowerManagement'
CONFIG_FILE_NAME = 'userConfig.ini'

position = 300, 100
childFrameDisplacement = 60,60
positionInPercent = 0,0

expandSize = 1180, 685
decreaseSize = 895, 245
portSettingsSize = 410, 300
grapgSettingsSize = 710, 300

version = '1.0.1.06'
date = '06.22.2018'

savePosition = True
saveSize = True
alwaysOnTop = True

import wx
onTopTrue = wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP
onTopFalse = wx.DEFAULT_FRAME_STYLE

childFrameStyle = wx.DEFAULT_FRAME_STYLE &~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX) | wx.FRAME_FLOAT_ON_PARENT

channelColour = '#eba6a1'

import configparser
import os, sys

import win32api
monitors = win32api.EnumDisplayMonitors()

def creatingDefaultConfigFile():
    configParser = configparser.ConfigParser()
    configParser['SAVING_CONFIG'] = {'saveSize': str(saveSize),
                                     'savePosition': str(savePosition),
                                     'alwaysOnTop': str(alwaysOnTop)}
    configParser['EXPAND_SIZE'] = {'expandWidth': str(expandSize[0]),
                                   'expandHeight' : str(expandSize[1])}
    configParser['DECREASE_SIZE'] = {'decreaseWidth': str(decreaseSize[0]),
                                     'decreaseHeight': str(decreaseSize[1])}
    configParser['POSITION'] = {'positionX': str(position[0]),
                                'positionY': str(position[1])}
    configParser['POSITION_IN_PERCENT'] = {'positionX': str(positionInPercent[0]),
                                           'positionY': str(positionInPercent[1])}
    pos = float(position[0]), float(position[1])
    style = onTopTrue
    with open(CONFIG_FILE_NAME, 'w') as configfile:
        configParser.write(configfile)
    return  pos, style

def GetConfigurations():
    if not os.path.exists(os.path.join(os.getcwd(), CONFIG_FILE_NAME)):
        pos, style = creatingDefaultConfigFile()
        expSize = expandSize
    else:
        configParser = configparser.ConfigParser()
        configParser.read(CONFIG_FILE_NAME)
        pos = getPosition(configParser)
        expSize = getExpandSize(configParser)
        style = getStyle(configParser)
    return wx.Point(pos), wx.Size(expSize), style

def getPosition(configParser):
    try:
        pos = float(configParser['POSITION']['positionX']), float(configParser['POSITION']['positionY'])
        if pos[0] > monitors[-1][2][2] or pos[1] > monitors[-1][2][3]:
            raise
    except:
        if type(KeyError()) == sys.exc_info()[0]:
            configParser['POSITION'] = {'positionX': str(position[0]),
                                        'positionY': str(position[1])}
            with open(CONFIG_FILE_NAME, 'w') as configfile:
                configParser.write(configfile)
        try:
            x_PercetPos = float(configParser['POSITION_IN_PERCENT']['positionX'])
            y_PercetPos = float(configParser['POSITION_IN_PERCENT']['positionY'])
            pos = monitors[0][2][2] / 100 * x_PercetPos, monitors[0][2][3] / 100 * y_PercetPos
        except KeyError:
            configParser['POSITION_IN_PERCENT'] = {'positionX': str(positionInPercent[0]),
                                                   'positionY': str(positionInPercent[1])}
            with open(CONFIG_FILE_NAME, 'w') as configfile:
                configParser.write(configfile)
        finally:
            x_PercetPos = float(configParser['POSITION_IN_PERCENT']['positionX'])
            y_PercetPos = float(configParser['POSITION_IN_PERCENT']['positionY'])
            pos = monitors[0][2][2] / 100 * x_PercetPos, monitors[0][2][3] / 100 * y_PercetPos
            configParser['POSITION'] = {'positionX': str(pos[0]),
                                        'positionY': str(pos[1])}
            with open(CONFIG_FILE_NAME, 'w') as configfile:
                configParser.write(configfile)
    return pos

def getStyle(configParser):
    try:
        onTop = configParser['SAVING_CONFIG']['alwaysOnTop']
    except KeyError as key:
        if 'alwaysOnTop' in str(key):
            configParser.set('SAVING_CONFIG', 'alwaysOnTop', str(alwaysOnTop))
        else:
            configParser['SAVING_CONFIG'] = {'saveSize': str(saveSize),
                                             'savePosition': str(savePosition),
                                             'alwaysOnTop': str(alwaysOnTop)}
        with open(CONFIG_FILE_NAME, 'w') as configFile:
            configParser.write(configFile)
    finally:
        onTop = configParser['SAVING_CONFIG']['alwaysOnTop']
    if 'True' in onTop:
        style = onTopTrue
    else:
        style = onTopFalse
    return style

def getExpandSize(configParser):
    try:
        expSize = int(configParser['EXPAND_SIZE']['expandWidth']), int(configParser['EXPAND_SIZE']['expandHeight'])
    except:
        configParser['EXPAND_SIZE'] = {'expandWidth': str(expandSize[0]),
                                       'expandHeight': str(expandSize[1])}
        with open(CONFIG_FILE_NAME, 'w') as configfile:
            configParser.write(configfile)
    finally:
        expSize = int(configParser['EXPAND_SIZE']['expandWidth']), int(configParser['EXPAND_SIZE']['expandHeight'])
    return expSize

def getDecreaseSize(configParser):
    try:
        decSize = int(configParser['DECREASE_SIZE']['decreaseWidth']), int(configParser['DECREASE_SIZE']['decreaseHeight'])
    except:
        configParser['DECREASE_SIZE'] = {'decreaseWidth': str(decreaseSize[0]),
                                         'decreaseHeight': str(decreaseSize[1])}
        with open(CONFIG_FILE_NAME, 'w') as configfile:
            configParser.write(configfile)
    finally:
        decSize = int(configParser['DECREASE_SIZE']['decreaseWidth']), int(configParser['DECREASE_SIZE']['decreaseHeight'])
    return decSize

def GetSavingConfig():
    configParser = configparser.ConfigParser()
    configParser.read(CONFIG_FILE_NAME)
    success = False
    while not success:
        try:
            configAlwaysOnTop = getAlwaysOnTop(configParser)

            configSaveSize = getSaveSize(configParser)

            configSavePosition = getSavePosition(configParser)

            configDecreaseSize = getDecreaseSize(configParser)

            configExpandSize = getExpandSize(configParser)
            success = True
        except KeyError as key:
            if 'saveSize' in str(key):
                configParser.set('SAVING_CONFIG', 'saveSize', str(saveSize))
            elif 'savePosition' in str(key):
                configParser.set('SAVING_CONFIG', 'savePosition', str(savePosition))
            elif 'decrease' in str(key):
                configParser.set('DECREASE_SIZE', 'decreaseWidth', str(decreaseSize[0]))
                configParser.set('DECREASE_SIZE', 'decreaseHeight', str(decreaseSize[1]))
            with open(CONFIG_FILE_NAME, 'w') as configFile:
                configParser.write(configFile)
    return configAlwaysOnTop, configSaveSize, configSavePosition, configDecreaseSize, configExpandSize

def getAlwaysOnTop(configParser):
    if 'True' in configParser['SAVING_CONFIG']['alwaysOnTop']:
        configAlwaysOnTop = True
    else:
        configAlwaysOnTop = False
    return configAlwaysOnTop

def getSaveSize(configParser):
    if 'True' in configParser['SAVING_CONFIG']['saveSize']:
        configSaveSize = True
    else:
        configSaveSize = False
    return configSaveSize

def getSavePosition(configParser):
    if 'True' in configParser['SAVING_CONFIG']['savePosition']:
        configSavePosition = True
    else:
        configSavePosition = False
    return configSavePosition

def SavingUsersConfig(window):
    configParser = configparser.ConfigParser()
    configParser.read(CONFIG_FILE_NAME)
    configParser.set('SAVING_CONFIG', 'saveSize', str(window.saveSize))
    configParser.set('SAVING_CONFIG', 'savePosition', str(window.savePosition))
    configParser.set('SAVING_CONFIG', 'alwaysOnTop', str(window.alwaysOnTop))
    if window.savePosition:
        pos = window.GetPosition()
        for monitor in monitors:
            if (pos[0] >= monitor[2][0] and pos[0] < monitor[2][2]) and (pos[1] >= monitor[2][1] and pos[1] < monitor[2][3]):
                x_PercetPos = (pos[0] - monitor[2][0]) * 100 / (monitor[2][2] - monitor[2][0])
                y_PercetPos = (pos[1] - monitor[2][1]) * 100 / (monitor[2][3] - monitor[2][1])
                try:
                    configParser.set('POSITION_IN_PERCENT', 'positionX', str(x_PercetPos))
                    configParser.set('POSITION_IN_PERCENT', 'positionY', str(y_PercetPos))
                except:
                    configParser['POSITION_IN_PERCENT'] = {'positionX': str(x_PercetPos),
                                                           'positionY': str(y_PercetPos)}
        configParser.set('POSITION', 'positionX', str(pos[0]))
        configParser.set('POSITION', 'positionY', str(pos[1]))
    if window.saveSize:
        if window.graphShown:
            window.expandSize = window.GetSize()
        configParser.set('EXPAND_SIZE', 'expandWidth', str(window.expandSize[0]))
        configParser.set('EXPAND_SIZE', 'expandHeight', str(window.expandSize[1]))
        if not window.graphShown:
            window.decreaseSize = window.GetSize()
        configParser.set('DECREASE_SIZE', 'decreaseWidth', str(window.decreaseSize[0]))
        configParser.set('DECREASE_SIZE', 'decreaseHeight', str(window.decreaseSize[1]))
    with open(CONFIG_FILE_NAME, 'w') as configFile:
        configParser.write(configFile)

def GetScreenCenter():
    x = monitors[0][2][2]
    y = monitors[0][2][3]
    return int(x/2), int(y/2)