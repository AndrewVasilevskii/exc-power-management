
class AppData(object):

    def __init__(self, channelsValues, filamentStatus, filamentCurrent, filamentMaxCurrent, connectionControlValue, directionValue):
        self.filamentStatus = filamentStatus
        self.channelsValues = channelsValues
        self.filamentCurrent = filamentCurrent
        self.filamentMaxCurrent = filamentMaxCurrent
        self.connectionControlValue = connectionControlValue
        self.directionValue = directionValue
        self.channelsNames = ['Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6', 'Channel7', 'Channel8', 'Filament']
        
    def getConnectionControlValue(self):
        with self.connectionControlValue.get_lock():
            return self.connectionControlValue.value

    def setConnectionControlValue(self, value):
        with self.connectionControlValue.get_lock():
            self.connectionControlValue.value = value
        
    def getFilamentStatus(self):
        with self.filamentStatus.get_lock():
            return self.filamentStatus.value

    def setFilamentStatus(self, value):
        with self.filamentStatus.get_lock():
            self.filamentStatus.value = value
        
    def getFilamentMaxCurrent(self):
        with self.filamentMaxCurrent.get_lock():
            return self.filamentMaxCurrent.value
        
    def setFilamentMaxCurrent(self, value):
        with self.filamentMaxCurrent.get_lock():
            self.filamentMaxCurrent.value = value
            
    def getFilamentCurrent(self):
        with self.filamentCurrent.get_lock():
            return self.filamentCurrent.value
        
    def setFilamentCurrent(self, value):
        with self.filamentCurrent.get_lock():
            self.filamentCurrent.value = value
    
    def getDirectionValue(self):
        with self.directionValue.get_lock():
            return self.directionValue.value
        
    def setDirectionValue(self, value):
        with self.directionValue.get_lock():
            self.directionValue.value = value
    
    def getChannelValue(self, channel):
        with self.channelsValues.get_lock():
            return self.channelsValues[channel]
        
    def setChannelValue(self, channel, value):
        with self.channelsValues.get_lock():
            self.channelsValues[channel] = value
            
    def getChannelName(self, channel):
        return self.channelsNames[channel]
    
    def setChannelName(self, channel, name):
        self.channelsNames[channel] = name