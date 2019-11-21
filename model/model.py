from multiprocessing import Value, Array
from threading import Thread
from model.appdata import AppData
from model.devicedata import DeviceData
from model.connector.autoconnector import AutoConnector
from model.pulldataloop import pullData

FILAMENT_CHANNEL = 8

import zipfile
import os

def zipfolder(foldername, target_dir):            
    zipobj = zipfile.ZipFile(foldername + '.zip', 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(target_dir) + 1
    for base, dirs, files in os.walk(target_dir):
        for file in files:
            fn = os.path.join(base, file)
            zipobj.write(fn, fn[rootlen:])

class Model(object):
    def __init__ (self, errorCB, onConnectCB, onCantReconnect):
        self.errorCB = errorCB
        self.onConnectCB = onConnectCB
        self.onCantReconnect = onCantReconnect
        
        channelsMaxValues = Array('i', 8)
        channelsMinValues = Array('i', 8)
        filamentRealCurrent = Value('d', 0.0)
        emissionValue = Value('d', 0.0)
        filamentActualVoltage = Value('d', 0.0)
        channelsRealValues = Array('d', 8)
        directionRealValue = Value('i', 1)
        
        filamentStatus = Value('i', 0)
        filamentRealStatus = Value('i', 0)
        
        for i in range(len(channelsMaxValues)):
            channelsMaxValues[i] = 60
            channelsMinValues[i] = -60
            channelsRealValues[i] = 0.0
                
        self.deviceData = DeviceData(channelsMaxValues, channelsMinValues, filamentRealStatus, filamentRealCurrent, filamentActualVoltage, emissionValue, channelsRealValues, directionRealValue)
        
        channelsValues = Array('d', 8)
        filamentCurrent = Value('d', 0.0)
        filamentMaxCurrent = Value('d', 2)
        connectionControlValue = Value('i', 0)
        directionValue = Value('i', 1)
        
        for i in range(len(channelsValues)):
            channelsValues[i] = 0.0
        
        self.appData = AppData(channelsValues, filamentStatus, filamentCurrent, filamentMaxCurrent, connectionControlValue, directionValue)

    def connect(self):
        self.autoConnecter = AutoConnector(self.errorCB, self.OnConnect, self.onCantReconnect)
        self.autoConnecter.connect()
        
    def connectWithParams(self, port, baudRate, parity, stopBits, flowControl):
        self.autoConnecter = AutoConnector(self.errorCB, self.OnConnect, self.onCantReconnect)
        self.autoConnecter.connectWithParams(port, baudRate, parity, stopBits, flowControl)

    def OnConnect(self, mips):
        self.mips = mips
        mips.disconnect()
        self.onConnectCB()
        self.pullProccess = Thread(target=pullData, args=(self.deviceData.channelsMaxValues, self.deviceData.channelsMinValues,
                                                                self.deviceData.filamentRealCurrent, self.deviceData.filamentActualVoltage, self.deviceData.emissionValue, self.deviceData.channelsRealValues, 
                                                                self.appData.channelsValues, self.appData.filamentCurrent, self.appData.filamentMaxCurrent, self.appData.connectionControlValue,
                                                                self.appData.filamentStatus, self.deviceData.filamentRealStatus, self.appData.directionValue, self.deviceData.directionRealValue,))
        self.pullProccess.daemon = True
        self.pullProccess.start()

    def filamentTrigger(self):
        if self.appData.getFilamentStatus() == 1:
            self.appData.setFilamentStatus(0)
            return 0
        else:
            self.appData.setFilamentStatus(1)
            return 1
        
    def directionTrigger(self):
        if self.deviceData.getDirectionRealValue() == 1:
            self.appData.setDirectionValue(0)
        else:
            self.appData.setDirectionValue(1)
        
    def isFilamentOn(self):
        return self.deviceData.getFilamentRealStatus() == 1

    def isDirectionFwd(self):
        return self.deviceData.getDirectionRealValue() == 1

    def getMaxValue(self, channel):
        if channel == FILAMENT_CHANNEL:
            return self.appData.getFilamentMaxCurrent()
        return self.deviceData.getChannelsMaxValues(channel)
    
    def getMinValue(self, channel):
        if channel == FILAMENT_CHANNEL:
            return 0
        return self.deviceData.getChannelsMinValues(channel)
    
    def getRealValue(self, channel):
        if channel == FILAMENT_CHANNEL:
            return self.deviceData.getFilamentRealCurrent()
        return self.deviceData.getChannelsRealValues(channel)
    
    def getEmission(self):
        return self.deviceData.getCurrentEmission()
    
    def getFilamentVoltage(self):
        return self.deviceData.getFilamentActualVoltage()
    
    def changeChannelName(self, channel, name):
        self.appData.setChannelName(channel, name)
        
    def getNameForChannel(self, channel):
        return self.appData.getChannelName(channel)
    
    def setChannelValue(self, channel, value):
        if channel == FILAMENT_CHANNEL:
            self.appData.setFilamentCurrent(value)
            return
        self.appData.setChannelValue(channel, value)

    def getChannelValue(self, channel):
        if channel == FILAMENT_CHANNEL:
            return self.appData.getFilamentCurrent()
        return self.appData.getChannelValue(channel)
