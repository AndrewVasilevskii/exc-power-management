import pickle

class ProfileData:
    def __init__(self):
        self.channelsValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.filamentValue = 0.0
        self.filamentMaxValue = 2.0
        self.directionValue = 1
        self.channelsNames = ['Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6', 'Channel7', 'Channel8', 'Filament']

class ProfileChannelsData:
    def __init__(self):
        self.channelsValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.filamentValue = 0.0
        self.filamentMaxValue = 2.0
        self.directionValue = 1
        self.channelsNames = ['Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6', 'Channel7', 'Channel8', 'Filament']

def saveChToFile(path, appData):
    profile = ProfileData()
    profile.channelsNames = appData.channelsNames
    profile.filamentMaxValue = appData.getFilamentMaxCurrent()
    profile.filamentValue = appData.getFilamentCurrent()
    profile.directionValue = appData.getDirectionValue()
    for x in range(0, 8):
        profile.channelsValues[x] = appData.getChannelValue(x)
    with open(path, "wb") as f:
        pickle.dump(profile, f, pickle.HIGHEST_PROTOCOL)
    
def loadChFromFile(path, appData, model):
    try:
        with open(path, "rb") as f:
            profile = pickle.load(f)
            appData.channelsNames = profile.channelsNames
            for x in range(0, 8):
                minVal = model.getMinValue(x)
                maxVal = model.getMaxValue(x)
                if profile.channelsValues[x] > maxVal:
                    appData.setChannelValue(x, maxVal)
                    # print("Channel-%s value = %s, changed to value = $s" % (x, profile.channelsValues[x], maxVal))
                elif profile.channelsValues[x] < minVal:
                    appData.setChannelValue(x, minVal)
                    # print("Channel-%s value = %s, changed to value = $s" % (x, profile.channelsValues[x], minVal))
                else:
                    appData.setChannelValue(x, profile.channelsValues[x])
    except Exception as e:
        if "no attribute \'channelsValues\'" in str(e):
            message = 'Profile damaged.\nThere is no \'channelsValues\' information in profile:\n%s' % path
        else:
            message = 'Unknown error acquired in profile:\n%s' % path
        log(e, path)
        import wx
        wx.MessageBox(message, 'Can\'t open profile', wx.OK | wx.ICON_ERROR)
        return wx.ID_CANCEL


class ProfileFilamentData:
    def __init__(self):
        self.filamentValue = 0.0
        self.filamentMaxValue = 2.0
        self.directionValue = 1
        self.filamentStatus = 0

def saveFilamentToFile(path, appData, filamentStatus):
    profile = ProfileFilamentData()
    profile.filamentMaxValue = appData.getFilamentMaxCurrent()
    profile.filamentValue = appData.getFilamentCurrent()
    profile.directionValue = appData.getDirectionValue()
    profile.filamentStatus = filamentStatus
    with open(path, "wb") as f:
        pickle.dump(profile, f, pickle.HIGHEST_PROTOCOL)


def loadFilamentFromFile(path, appData):
    try:
        with open(path, "rb") as f:
            profile = pickle.load(f)
            appData.setFilamentMaxCurrent(profile.filamentMaxValue)
            appData.setFilamentCurrent(profile.filamentValue)
            appData.setDirectionValue(profile.directionValue)
            # appData.setFilamentStatus(profile.filamentStatus)
    except Exception as e:
        message = 'Unknown error acquired in profile:\n%s' % path
        log(e, path)
        import wx
        wx.MessageBox(message, 'Can\'t open profile', wx.OK | wx.ICON_ERROR)
        return wx.ID_CANCEL


def log(exception, path):
    import logging
    log_file = 'profile.log'
    logger = logging.getLogger('profile')
    hdlr = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s ----- %(levelname)s ----- %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.ERROR)
    logger.error(str(exception) + ' in file:   ' + path)