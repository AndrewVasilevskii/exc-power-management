

class DeviceData(object):
    def __init__ (self, channelsMaxValues, channelsMinValues, filamentRealStatus, filamentRealCurrent, filamentActualVoltage, emissionValue, channelsRealValues, directionRealValue):
        self.channelsMaxValues = channelsMaxValues
        self.channelsMinValues = channelsMinValues
        self.filamentRealCurrent = filamentRealCurrent
        self.emissionValue = emissionValue
        self.channelsRealValues = channelsRealValues
        self.filamentActualVoltage = filamentActualVoltage
        self.filamentRealStatus = filamentRealStatus
        self.directionRealValue = directionRealValue
        
    def getChannelsMaxValues(self, channel):
        with self.channelsMaxValues.get_lock():
            return self.channelsMaxValues[channel]
        
    def setChannelsMaxValues(self, channel, value):
        with self.channelsMaxValues.get_lock():
            self.channelsMaxValues[channel] = value
            
    def getChannelsMinValues(self, channel):
        with self.channelsMinValues.get_lock():
            return self.channelsMinValues[channel]
        
    def setChannelsMinValues(self, channel, value):
        with self.channelsMinValues.get_lock():
            self.channelsMinValues[channel] = value
                
    def getFilamentRealCurrent(self):
        with self.filamentRealCurrent.get_lock():
            return self.filamentRealCurrent.value
        
    def setFilamentRealCurrent(self, value):
        with self.filamentRealCurrent.get_lock():
            self.filamentRealCurrent.value = value

    def getFilamentRealStatus(self):
        with self.filamentRealStatus.get_lock():
            return self.filamentRealStatus.value
        
    def setFilamentRealStatus(self, value):
        with self.filamentRealStatus.get_lock():
            self.filamentRealStatus.value = value
            
    def getDirectionRealValue(self):
        with self.directionRealValue.get_lock():
            return self.directionRealValue.value
        
    def setDirectionRealValue(self, value):
        with self.directionRealValue.get_lock():
            self.directionRealValue.value = value
            
    def getChannelsRealValues(self, channel):
        with self.channelsRealValues.get_lock():
            return self.channelsRealValues[channel]
        
    def setChannelsRealValues(self, channel, value):
        with self.channelsRealValues.get_lock():
            self.channelsRealValues[channel] = value
    
    def getCurrentEmission(self):
        with self.emissionValue.get_lock():
            return self.emissionValue.value
    
    def setCurrentEmission(self, value):
        with self.emissionValue.get_lock():
            self.emissionValue.value = value
            
    def getFilamentActualVoltage(self):
        with self.filamentActualVoltage.get_lock():
            return self.filamentActualVoltage.value
    
    def setFilamentActualVoltage(self, value):
        with self.filamentActualVoltage.get_lock():
            self.filamentActualVoltage.value = value    
